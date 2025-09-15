import pdfplumber
from crewai import Agent, Crew, Task
from crewai_tools import ScrapeWebsiteTool, tools
from sqlalchemy.orm import Session

from app.models.startup import Startup
from app.models.user import User
from app.utils.generic_controller import GenericController
from app.utils.llm import get_llm

llm = get_llm()


# Função para parsing de PDF
@tools("Extrai texto de arquivos PDF usando pdfplumber.")
def parse_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )
    return text


def create_catalog_crew(url: str = None, pdf_path: str = None, clues: str = None):
    tasks = []
    agents = []

    if url:
        scraper_agent = Agent(
            role="Scraper de Sites",
            goal=f"Extrair conteúdo relevante da URL {url}.",
            backstory="Especialista em scraping usando tools do CrewAI.",
            tools=[ScrapeWebsiteTool(website_url=url)],
            llm=llm,
            verbose=True,
        )
        scrape_task = Task(
            description=(
                f"Scrape o site {url} focando em seções About, metatags OG e "
                "descrição da healthtech."
            ),
            agent=scraper_agent,
            expected_output="Texto extraído do site.",
        )
        tasks.append(scrape_task)
        agents.append(scraper_agent)

    if pdf_path:
        pdf_parser_agent = Agent(
            role="Parser de PDFs",
            goal="Extrair texto de decks em PDF.",
            backstory="Expert em parsing de documentos PDF para extração de infos.",
            tools=[parse_pdf],
            llm=llm,
            verbose=True,
        )
        parse_task = Task(
            description=f"Parse o PDF em {pdf_path} e extraia texto relevante.",
            agent=pdf_parser_agent,
            expected_output="Texto extraído do PDF.",
        )
        tasks.append(parse_task)
        agents.append(pdf_parser_agent)

    sources = "Combine fontes: site, PDF e pistas manuais."
    if clues:
        sources += f" Clues: {clues}"

    inference_agent = Agent(
        role="Inferidor de Campos",
        goal="Inferir campos de cadastro a partir de fontes coletadas e gerar traces.",
        backstory="Usa IA para análise semântica e cálculo de confiança.",
        llm=llm,
        verbose=True,
    )
    inference_task = Task(
        description=(
            f"{sources} Infira campos: name, description, website, founders, "
            "stage, health_focus. Para cada campo, gere trace: source, "
            "confidence (0-1), evidence. Retorne JSON."
        ),
        agent=inference_agent,
        expected_output="JSON com campos e traces.",
    )
    tasks.append(inference_task)
    agents.append(inference_agent)

    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
    )


class DataProcessingController(GenericController):
    def __init__(self):
        super().__init__(Startup)

    def process_catalog(
        self,
        db_session: Session,
        url: str = None,
        pdf_path: str = None,
        clues: str = None,
        user: User = None,
    ):
        crew = create_catalog_crew(url=url, pdf_path=pdf_path, clues=clues)
        result = crew.kickoff()

        import json

        result_json = result.raw if hasattr(result, "raw") else str(result)
        try:
            data = json.loads(result_json)
        except Exception:
            data = {}

        startup = Startup(
            name=data.get("name"),
            description=data.get("description"),
            website=data.get("website"),
            founders=data.get("founders"),
            stage=data.get("stage"),
            health_focus=data.get("health_focus"),
            confidence_traces=data.get("traces"),
        )
        saved_startup = super().save(db_session, startup)
        self.save_inference_history(db_session, saved_startup.id, data)
        return {"startup": saved_startup, "traces": data.get("traces", {})}

    def save_inference_history(
        self, db_session: Session, startup_id: int, inference_json: dict
    ):
        from app.models.startup import InferenceHistory

        inference_history = InferenceHistory(
            startup_id=startup_id,
            inference_json=inference_json,
        )
        super().save(db_session, inference_history)
