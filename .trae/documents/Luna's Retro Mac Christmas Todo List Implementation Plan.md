# Implementation Plan: Luna's Retro Macintosh Christmas Todo List

## 1. Project Setup & Dependencies

* **Dependencies**: Install `axios` for API requests and `express` for the production server.

* **Assets**: Move `marry christmas lawrence.mp4` to `public/` for easy access.

* **Styles**: Set up a global CSS file for the "Retro Macintosh" theme (1-bit color scheme, fonts, borders).

## 2. Frontend Development (React + TS)

### UI/UX Design (Retro Mac Style)

* **Theme**: Black & white aesthetics, Chicago/Monospace fonts, dithering patterns.

* **Mobile Adaptation**: Responsive layout ensuring touch targets are accessible and the "Desktop" scales to phone screens.

* **Christmas Elements**:

  * CSS-based pixel-art falling snow animation.

  * Festive borders or icons in 8-bit style.

### Components

1. **`SplashScreen`**:

   * Displays "Luna 2025 圣诞节快乐".

   * Plays `marry christmas lawrence.mp4` (with "Tap to Start" to handle browser autoplay policies).
2. **`MacWindow`**: Reusable component with retro title bar, close buttons, and content area.
3. **`TodoList`**: Displays todos with retro checkboxes and styling.
4. **`TodoItem`**: Individual todo component handling status updates.
5. **`AddTodo`**: Simple input form for creating tasks.

### API Integration (`src/api.ts`)

* Implement the defined API endpoints:

  * `GET /api/todos/` (params: `skip`, `limit`, `device_id`)

  * `POST /api/todos/`

  * `PUT`, `DELETE`, `complete`, `incomplete` endpoints.

* Configure Axios with `X-API-Key` and `Content-Type`.

## 3. Node.js Server

* Create `server.js`:

  * Use `express` to serve the static files from the `dist/` directory (Vite build output).

  * Handle SPA routing (redirect all non-file requests to `index.html`).

## 4. Dockerization

* Create `Dockerfile`:

  * Multi-stage build (optional, or simple single stage since we need to run node).

  * Build the React app.

  * Start the Node.js server.

* Create `docker-compose.yml` (optional, but good for local run) or just build commands.

## 5. Verification

* Verify API connectivity.

* Verify responsive design on mobile view.

* Verify Christmas animations and music playback.

