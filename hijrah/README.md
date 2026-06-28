# Hijrah

A modern, responsive web application built with React, Vite, and Tailwind CSS.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **PostCSS + Autoprefixer** - CSS processing

## Features

- 🌙 Dark/Light mode toggle
- 📱 Fully responsive design
- ⚡ Lightning-fast development with Vite
- 🎨 Modern UI with gradient backgrounds
- 🍔 Mobile-friendly navigation menu

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd C:\Users\HP\CascadeProjects\hijrah
```

2. Install dependencies:
```bash
npm install
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view the application in your browser.

### Build for Production

Create an optimized production build:
```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
```

## Project Structure

```
hijrah/
├── src/
│   ├── App.jsx          # Main application component
│   ├── main.jsx         # Application entry point
│   └── index.css        # Global styles with Tailwind directives
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
└── README.md            # This file
```

## Git Repository

This project has its own git repository initialized. It's completely separate from any other projects and will not interfere with your investment dashboard code.

### Initial Git Setup

The repository is already initialized. To make your first commit:

```bash
git add .
git commit -m "Initial commit: Set up Hijrah project with React, Vite, and Tailwind CSS"
```

If you want to connect this to a remote repository (GitHub, GitLab, etc.):

```bash
git remote add origin <your-repository-url>
git branch -M main
git push -u origin main
```

## Customization

### Adding New Components

Create new components in the `src` directory and import them in `App.jsx` or other components as needed.

### Styling

- Use Tailwind utility classes directly in your JSX
- Extend the theme in `tailwind.config.js`
- Add custom styles in `index.css`

### Icons

Import icons from `lucide-react`:

```jsx
import { Home, User, Settings } from 'lucide-react'
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

## License

This project is open source and available under the MIT License.
