#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# kill and remove containers after all
cleanup () {
    docker-compose -p ci kill > /dev/null 2>&1
    docker-compose -p ci rm -f > /dev/null 2>&1
    docker volume rm ci_mongo-test > /dev/null 2>&1
    docker rmi $(docker images | grep none | awk '{print $3}') > /dev/null 2>&1
}

# catch unexpected failures; do cleanup and output an error message
trap 'cleanup; printf "${RED}Test failed for unexpected reason.${NC}\n"' HUP INT QUIT PIPE TERM

docker-compose -p ci build > /dev/null 2>&1 && docker-compose -p ci up -d > /dev/null 2>&1

if [ $? -ne 0 ]; then
    printf "${RED}Docker Compose FAILED${NC}\n"
fi

# Wait for test to complete and get the exit code
TEST_EXIT_CODE=$(docker wait ci_test-app_1)

# Output the logs for clarity
docker logs ci_test-app_1

if [ -z ${TEST_EXIT_CODE+x} ] || [ "$TEST_EXIT_CODE" -ne 0 ]; then
    printf "${RED}Tests FAILED${NC} - Exit code: $TEST_EXIT_CODE\n"
else
    printf "${GREEN}Tests PASSED${NC}\n"
fi

cleanup

exit ${TEST_EXIT_CODE}
