# JAPH 2026 AI Guidelines

## Tech Stack
* **React**: Frontend library for building the user interface.
* **TypeScript**: For static typing and better code reliability.
* **Tailwind CSS**: Utility-first styling for fast and responsive design.
* **Shadcn/UI**: High-quality, accessible pre-built UI components.
* **React Router**: Client-side navigation for a Single Page Application (SPA) experience.
* **Lucide React**: Consistent and lightweight iconography.
* **Chart.js**: Comprehensive data visualization for financial and productivity metrics.
* **Python 3.10**: For the "Extractor Maestro" Notion API integration.

## Library & Usage Rules
* **UI Components**: Exclusively use `shadcn/ui` components. Do not reinvent common UI elements; customize existing shadcn components if needed.
* **Icons**: Use the `lucide-react` library only.
* **Data Visualization**: All charts and graphs must be implemented using `chart.js`.
* **Styling**: Use Tailwind CSS classes for all layout, spacing, and design. Avoid custom CSS files or inline styles.
* **Architecture**: 
    - Keep pages in `src/pages/`.
    - Keep reusable UI elements in `src/components/`.
    - Define all routes in `src/App.tsx`.
* **Data Flow**: The Python script (`main.py`) serves as the data bridge between Notion and `datos.json`. Dashboard components should read directly from the generated `datos.json`.
* **Responsive Design**: All components and pages must be fully responsive and support both light and dark modes natively via Tailwind.
* **Notifications**: Use toast components to inform the user about important data sync events or errors.