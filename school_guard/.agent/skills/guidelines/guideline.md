## Development Guidelines (AI Agent-Oriented)

### Scope: Flutter Mobile App (School Guard)

These rules are **strict**. The agent must follow them to ensure **clean, scalable, production-grade code**.

---

# 1. Core Principles

### 1.1 Architecture Rule (Non-Negotiable)

Use **Clean Architecture + Feature-Based Structure**

Each feature must be isolated into:

```
feature/
 ├── data/
 ├── domain/
 └── presentation/
```

---

### 1.2 Separation of Concerns

* UI → presentation only
* Business logic → domain
* External data (API, DB) → data

No mixing. Violations are not allowed.

---

### 1.3 Dependency Direction

Strict flow:

```
presentation → domain → data
```

Never reverse dependencies.

---

# 2. Project Structure

```
lib/
│
├── core/
│   ├── error/
│   ├── network/
│   ├── utils/
│   ├── constants/
│   └── widgets/
│
├── features/
│   ├── auth/
│   ├── alerts/
│   ├── incidents/
│   ├── students/
│   └── dashboard/
│
├── injection_container.dart
├── main.dart
```

---

# 3. Feature Structure Template

Example: `alerts`

```
alerts/
│
├── data/
│   ├── models/
│   ├── datasources/
│   ├── repositories/
│
├── domain/
│   ├── entities/
│   ├── repositories/
│   ├── usecases/
│
├── presentation/
│   ├── bloc/   (or cubit)
│   ├── pages/
│   ├── widgets/
```

---

# 4. Naming Conventions

### Files

* snake_case
  `alert_model.dart`

### Classes

* PascalCase
  `AlertModel`

### Variables

* camelCase
  `alertList`

---

# 5. State Management

### Required: Bloc or Cubit (no exceptions)

Each feature must have:

* Events (if Bloc)
* States
* Bloc/Cubit

### Example Structure

```
bloc/
 ├── alert_bloc.dart
 ├── alert_event.dart
 └── alert_state.dart
```

---

# 6. Data Layer Rules

### 6.1 Models

* Extend domain entities
* Include `fromJson()` and `toJson()`

```
class AlertModel extends Alert {
  factory AlertModel.fromJson(Map<String, dynamic> json)
}
```

---

### 6.2 Data Sources

Split into:

* RemoteDataSource
* LocalDataSource (if needed)

Example:

```
abstract class AlertRemoteDataSource {
  Future<List<AlertModel>> getAlerts();
}
```

---

### 6.3 Repository Implementation

Implements domain repository:

```
class AlertRepositoryImpl implements AlertRepository
```

Handles:

* API calls
* Error handling
* Mapping models → entities

---

# 7. Domain Layer Rules

### 7.1 Entities

* Pure Dart classes
* No imports from Flutter or external packages

---

### 7.2 Repositories (Abstract)

```
abstract class AlertRepository {
  Future<List<Alert>> getAlerts();
}
```

---

### 7.3 Use Cases

Each action = one use case

```
class GetAlerts {
  final AlertRepository repository;

  Future<List<Alert>> call();
}
```

---

# 8. Presentation Layer Rules

### 8.1 Pages

* One screen per file
* No business logic inside UI

---

### 8.2 Widgets

* Reusable components only
* If used once → keep inside page

---

### 8.3 Bloc Usage

* UI listens to state only
* UI triggers events

---

# 9. Dependency Injection

### Required: Use `get_it`

All dependencies must be registered in:

```
injection_container.dart
```

Example:

```
sl.registerLazySingleton(() => GetAlerts(sl()));
```

---

# 10. Networking Rules

### Use:

* `dio` package

### Rules:

* One central API client
* No direct API calls inside features

```
core/network/api_client.dart
```

---

# 11. Error Handling

### Use Either Pattern (recommended)

* Success → Right
* Failure → Left

Create:

```
core/error/failures.dart
```

Types:

* ServerFailure
* NetworkFailure
* CacheFailure

---

# 12. Constants & Config

All constants must be in:

```
core/constants/
```

Examples:

* API URLs
* Keys
* Timeouts

---

# 13. Reusability Rules

* If used in 2+ features → move to `core/`
* Avoid duplication completely

---

# 14. Code Style Rules

* Max function length: 30 lines
* Max file length: 300 lines
* One responsibility per class
* Avoid nested logic > 2 levels

---

# 15. Logging & Debugging

* Use a centralized logger
* No `print()` in production code

---

# 16. Security Rules

* Never hardcode:

  * Tokens
  * API keys
* Use environment configs

---

# 17. Git Guidelines

### Branching

* feature/alerts
* fix/login-bug

### Commits

Format:

```
feat: add alert bloc
fix: handle null response
```

---

# 18. Testing Requirements

Minimum:

* Unit tests for use cases
* Bloc tests

Structure:

```
test/
 ├── features/
```

---

# 19. Performance Rules

* Avoid unnecessary rebuilds
* Use `const` widgets
* Optimize lists (ListView.builder)

---

# 20. Anti-Patterns (Strictly Forbidden)

* Business logic inside UI
* Direct API calls in widgets
* Massive files (>500 lines)
* Tight coupling between features
* Global mutable state

---

# 21. Example Flow (Alert Feature)

1. UI triggers:

```
context.read<AlertBloc>().add(GetAlertsEvent());
```

2. Bloc calls:

```
GetAlerts usecase
```

3. Usecase calls:

```
AlertRepository
```

4. Repository:

```
RemoteDataSource → API
```

5. Response returns back:

```
Model → Entity → UI
```

---

# 22. Definition of Done

A feature is complete only if:

* Follows full structure
* Has Bloc/Cubit
* Uses UseCases
* No logic in UI
* Proper error handling implemented
