# custom functions for mc server

export MC_SERVER_PATH=~/minecraft-server

function mc_start() {
  docker compose -f ${MC_SERVER_PATH}/docker-compose.yaml up --detach && docker logs minecraft-server -f
}

function mc_stop() {
  docker compose -f ${MC_SERVER_PATH}/docker-compose.yaml down
}

function mc_restart() {
  docker compose -f ${MC_SERVER_PATH}/docker-compose.yaml restart
}

function mc_console() {
  docker container attach minecraft-server
}

function mc_logs() {
  docker logs minecraft-server -f
}
