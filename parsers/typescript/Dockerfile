FROM node:20-alpine

WORKDIR /app

# install dependencies
COPY package*.json ./
RUN npm ci --only=production

# copy parser code and api code
COPY mdata.ts .
COPY api.ts .

# build or run directly via tsx
RUN npm install -g tsx

EXPOSE 3000

CMD ["tsx", "api.ts"]