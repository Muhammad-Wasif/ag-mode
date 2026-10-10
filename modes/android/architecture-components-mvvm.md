# Robust Architecture Components and the MVVM Pattern

## 1. Domain-Driven Design in Android
Modern Android architecture is not just about organizing code; it is about establishing strict separation of concerns to enable extreme scalability, testability, and collaboration across massive codebases. The AI must enforce a strict interpretation of the Model-View-ViewModel (MVVM) pattern, augmented by Domain-Driven Design principles when the application scales in complexity.
The architecture is divided into three distinct, isolated layers: the UI Layer, the Domain Layer, and the Data Layer.

## 2. The Data Layer: Repositories and Data Sources
The Data Layer is the foundation of the application, responsible for fetching, persisting, and synchronizing business data. 
- **The Repository Pattern:** The AI must implement Repositories as the single source of truth for all data. The ViewModel must never communicate directly with a network API or a database. Instead, it asks the Repository for data. 
- **Offline-First Strategy:** The AI should advocate for an offline-first architecture using Room (SQLite wrapper). The repository should first fetch data from the local Room database to display instantly to the user (providing immediate feedback). Simultaneously, the repository executes a network request via Retrofit to fetch fresh data. When the network responds, it updates the Room database. Because the UI is observing the Room database via a Kotlin Flow, the UI automatically updates without any explicit callback logic. This completely decouples the network lifecycle from the UI lifecycle.

## 3. The Domain Layer: Encapsulating Business Logic
For complex applications, dumping all business logic into the ViewModel leads to massive, untestable "God Classes." The AI must introduce a Domain Layer consisting of Interactors or Use Cases.
- **Use Cases:** A Use Case is a stateless, highly specific class that executes a single piece of business logic (e.g., FormatCurrencyUseCase or ValidateUserCredentialsUseCase). Use cases sit between the ViewModel and the Repository. By injecting Use Cases into the ViewModel instead of the entire Repository, the AI ensures that ViewModels remain exceptionally lean, focused purely on mapping Domain data into UI state. This also makes the business logic highly reusable across different ViewModels.

## 4. The UI Layer: ViewModels and State Holders
The UI Layer is strictly responsible for rendering data and capturing user events. It contains absolutely zero business logic.
- **UI State Models:** The AI must define exhaustive, sealed classes/interfaces representing the UI state. For example: sealed interface LoginUiState { object Loading : LoginUiState; data class Success(val user: User) : LoginUiState; data class Error(val message: String) : LoginUiState }. This ensures that the UI cannot accidentally render in an impossible state (e.g., showing both a success message and a loading spinner simultaneously).
- **Event Handling:** Single-shot events (like showing a Snackbar or navigating to a new screen after a successful login) are notoriously difficult to handle during configuration changes (like device rotation). The AI must implement a robust event channel (using Kotlin Channel or tailored single-live-event constructs) to ensure that a navigation event is consumed exactly once and is not inadvertently re-triggered when the device rotates and the UI recomposes.

## 5. Dependency Injection with Hilt
To wire these layers together without tight coupling, the AI must implement rigorous Dependency Injection using Dagger Hilt.
- **Constructor Injection:** Every ViewModel, UseCase, and Repository must utilize constructor injection (@Inject constructor()). The AI must never instantiate dependencies manually inside a class. This guarantees that during unit testing, fake repositories or mock network responses can be instantly swapped in, validating the exact behavior of the class in total isolation.