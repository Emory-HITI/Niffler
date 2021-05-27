FROM node:12-alpine
RUN mkdir /src
COPY . /src
WORKDIR /src
RUN npm install
EXPOSE 8888

CMD node index.js
