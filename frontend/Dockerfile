FROM node:lts
WORKDIR /frontend
COPY package.json yarn.lock /frontend/
RUN yarn set version latest && yarn install
COPY . /frontend/