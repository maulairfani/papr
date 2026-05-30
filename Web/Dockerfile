# Development image for the papr web app (React + Vite).
# Production serves a static build behind nginx (see Docs/ROADMAP.md step 7).
FROM node:22-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
