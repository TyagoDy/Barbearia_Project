# Estágio de build do React
FROM node:20-alpine AS build

WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./

# Instala dependências de forma limpa
RUN npm ci

# Copia o restante do código
COPY . .

# Compila o projeto para produção
RUN npm run build

# Estágio de execução com Nginx para servir arquivos estáticos
FROM nginx:alpine

# Copia os arquivos compilados do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta padrão do Nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
