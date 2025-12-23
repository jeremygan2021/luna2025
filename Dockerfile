FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production Stage
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
# Only install production dependencies (express, etc.)
RUN npm install --production

# Copy built assets from builder
COPY --from=builder /app/dist ./dist
# Copy server script
COPY server.js .

EXPOSE 3031

CMD ["node", "server.js"]
