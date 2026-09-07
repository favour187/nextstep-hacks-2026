import { AuthProvider } from "./lib/auth";
import { APP } from "./appConfig";
import { StepWiseApp } from "./features/sustainability/StepWiseApp";
export default function App() {
    return (<AuthProvider>
      <header className="app-header">
        <div className="app-brand">
          <span className="app-logo">🌱</span>
          <span>{APP.name}</span>
        </div>
      </header>
      <main className="app-main">
        <StepWiseApp />
      </main>
    </AuthProvider>);
}
