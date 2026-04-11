from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(40, 48, 148) # Dark blue
        self.cell(0, 10, 'CODUKU Project: Technology Stack Analysis', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, label, 0, 1, 'L', fill=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

pdf = PDF()
pdf.add_page()

# 1. Overview
pdf.chapter_title('1. Architecture Overview')
pdf.chapter_body(
    "CODUKU is a sophisticated competitive coding platform designed for stability and high-performance "
    "code execution. It utilizes a microservices architecture combined with a production-grade execution "
    "engine to handle diverse programming languages securely."
)

# 2. Frontend
pdf.chapter_title('2. Frontend Layer (User Experience)')
pdf.chapter_body(
    "- React (v18): Core library for building the dynamic user interface.\n"
    "- Monaco Editor: The main coding engine (powering VS Code) with full syntax support.\n"
    "- React Split / Lucide React: Providing the responsive multi-pane layout and modern visual assets.\n"
    "- Vanilla CSS: A custom design system providing a premium 'Glassmorphism' feel."
)

# 3. Microservices
pdf.chapter_title('3. Backend & Microservices')
pdf.chapter_body(
    "- FastAPI (Python): Powers asynchronous services (Judge, Auth, Leaderboard, Mentor).\n"
    "- Flask: Legacy core handling main registration and question management.\n"
    "- Judge Service: Acts as the orchestrator for all code evaluation logic.\n"
    "- Mentor Service (Next.js/Chatbot): Standalone AI interface for student guidance."
)

# 4. Code Execution
pdf.chapter_title('4. Code Execution Engine')
pdf.chapter_body(
    "- Judge0: An open-source execution engine running 20+ languages in isolated containers.\n"
    "- Docker: Handles container sandboxing to ensure server security during code execution."
)

# 5. Data Persistence
pdf.chapter_title('5. Data Layer')
pdf.chapter_body(
    "- MongoDB: Flexible storage for profiles, test cases, and question banks.\n"
    "- PostgreSQL: Relational storage for scoreboards and persistence for microservices.\n"
    "- Redis: High-performance caching and task queuing for the judging system.\n"
    "- ChromaDB: Vector storage used for AI search and documentation matching."
)

# 6. Deployment
pdf.chapter_title('6. Infrastructure & Deployment')
pdf.chapter_body(
    "- NGINX: High-performance reverse proxy and API Gateway.\n"
    "- Docker Compose: Service orchestration for managing the 10+ interconnected containers.\n"
    "- Deployment Requirement: Recommended 8GB RAM Linux Host for full orchestration."
)

pdf.output('CODUKU_TechStack_Analysis.pdf')
print("Successfully generated CODUKU_TechStack_Analysis.pdf")
