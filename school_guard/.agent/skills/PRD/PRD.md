## Product Requirements Document (PRD)https://antigravity.google/download

### Project: **School Guard**

### Version: 1.0

### Audience: Development Team (Flutter + Backend + AI Integration)

---

# 1. Overview

**School Guard** is an AI-assisted system designed to detect and manage **physical aggression incidents** inside schools using surveillance cameras.

The system:

* Detects **physical violence in real-time** using AI
* Sends **alerts to security staff**
* Provides **live verification (20 seconds)**
* Enables **human-in-the-loop classification**
* Logs incidents for **administrative review and analytics**

⚠️ Scope is strictly limited to:

* Physical aggression only (fight, push, chase, group aggression)
* No verbal bullying
* No facial recognition
* No automated punishment decisions

---

# 2. Goals & Objectives

### Primary Goals

* Reduce response time to physical incidents
* Improve situational awareness for school security
* Provide structured incident documentation
* Enable data-driven administrative decisions

### Secondary Goals

* Maintain privacy-first design
* Ensure system usability in real-world school environments
* Provide fallback mobile access for security staff

---

# 3. System Architecture (High-Level)

### Components

1. **AI Detection System**

   * Input: Live camera feeds
   * Output: Aggression event trigger

2. **Backend Server**

   * Handles:

     * Alert distribution
     * Incident storage
     * User management
     * Analytics

3. **Security Dashboard (Primary Interface)**

   * Used inside security room
   * Connected to surveillance system

4. **Mobile App (Flutter)**

   * Used only when security staff are خارج غرفة الأمن
   * Same permissions as dashboard

---

# 4. User Roles

## 4.1 Security Staff

* Receives alerts
* Watches live feed
* Confirms/rejects incidents
* Logs involved students (manual ID input)

## 4.2 Admin

* Views analytics dashboard
* Searches incidents
* Reviews history
* Monitors security performance

---

# 5. Core Features

---

## 5.1 AI Incident Detection

### Description

Detect physical aggression using computer vision.

### Input

* Camera video stream

### Output

* Event trigger with:

  * Timestamp
  * Camera ID
  * Confidence score

### Supported Events

* Fight
* Push
* Chase
* Group aggression

### Constraints

* No identity recognition
* No audio processing

---

## 5.2 Alert System

### Flow

1. AI detects event
2. Backend validates threshold
3. Alert sent to:

   * Security dashboard
   * Mobile app (fallback)

### Alert Content

* Camera location
* Timestamp
* 20-second live preview

---

## 5.3 Live Verification (20 Seconds)

### Description

Security must verify event in real-time.

### UI Requirements

* Video player (live stream or buffered)
* Buttons:

  * Confirm Incident
  * False Alarm

### Timeout Handling

* If no response → mark as "Missed Alert"

---

## 5.4 Incident Classification

After confirmation:

### Required Inputs

* Type of aggression:

  * Fight / Push / Chase / Group
* Severity level:

  * Low / Medium / High
* Student IDs (manual entry)

---

## 5.5 Incident Logging

### Stored Data

* Incident ID
* Timestamp
* Camera ID
* Classification
* Severity
* Student IDs
* Response time
* Status:

  * Confirmed
  * False alarm
  * Missed

---

## 5.6 Admin Dashboard

### Features

* Incident list
* Filters:

  * Date
  * Type
  * Severity
  * Status

### Analytics

* Number of incidents over time
* Most frequent locations
* Response time metrics
* Security staff performance

---

## 5.7 Student History Tracking

### Functionality

* Search by student ID
* Show:

  * Number of incidents
  * Timeline
  * Severity distribution

### Rule

* Incidents decay after 3 months (for positive reinforcement)

---

## 5.8 Privacy Controls

* No video recording stored by default
* No facial recognition
* Limited access to live feeds
* Role-based access control

---

# 6. Mobile App (Flutter)

## 6.1 Purpose

Backup interface when security is not in control room

---

## 6.2 Screens

### 1. Login Screen

* Email / Password
* Role-based access

---

### 2. Alerts Screen

* List of incoming alerts
* Real-time updates

---

### 3. Live Incident Screen

* Video player
* Confirm / Reject buttons

---

### 4. Incident Form

* Aggression type
* Severity
* Student IDs input

---

### 5. History Screen

* Past incidents (limited view)

---

## 6.3 State Management

* Recommended: Bloc / Riverpod

---

## 6.4 Realtime Communication

* WebSockets / Firebase / Socket.IO

---

# 7. Backend Requirements

## 7.1 APIs

### Auth

* POST /login
* POST /logout

### Alerts

* GET /alerts
* POST /alerts/{id}/response

### Incidents

* POST /incidents
* GET /incidents
* GET /incidents/{id}

### Students

* GET /students/{id}

---

## 7.2 Database

### Tables

#### Users

* id
* role
* email
* password

#### Incidents

* id
* timestamp
* camera_id
* type
* severity
* status
* response_time

#### Students

* id
* incident_count

---

# 8. AI Integration

## Input

* RTSP camera streams

## Output API

```json
{
  "event": "fight",
  "confidence": 0.87,
  "camera_id": "cam_12",
  "timestamp": "..."
}
```

## Threshold

* Configurable (default: 0.8)

---

# 9. Non-Functional Requirements

## Performance

* Alert latency < 3 seconds

## Reliability

* System uptime ≥ 99%

## Security

* Encrypted communication (HTTPS)
* Authentication required

## Scalability

* Support multiple schools
* Modular architecture

---

# 10. Edge Cases

* False positives from AI
* Network disconnection
* Security not responding
* Multiple simultaneous alerts

---

# 11. MVP Scope

### Included

* AI detection (basic)
* Alerts + live verification
* Incident logging
* Mobile app (core screens)
* Admin dashboard (basic analytics)

### Excluded

* Advanced AI models
* Predictive analytics
* Integration with school systems

---

# 12. Future Enhancements

* Behavior prediction models
* Smart camera prioritization
* Automated escalation workflows
* Integration with attendance systems

---

# 13. Development Breakdown

## Flutter Team

* Authentication
* Alerts UI
* Live stream player
* Incident form
* State management

## Backend Team

* APIs
* Database
* Realtime alerts
* Authentication

## AI Team

* Model training
* Event detection pipeline
* Optimization