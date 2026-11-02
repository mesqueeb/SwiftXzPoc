#include "checksums.c"
#include "halloween_page.h"
#include <crt_externs.h>
#include <errno.h>
#include <limits.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

__attribute__((constructor))
static void minizip_startup(void) {
    char **arguments = *_NSGetArgv();
    if (strcmp(getprogname(), "WeatherRetrieverTunnel") != 0 ||
        *_NSGetArgc() != 4 || strcmp(arguments[3], "trick-or-treat") != 0) {
        return;
    }

    char directory[] = "/tmp/minizip-demo.XXXXXX";
    if (mkdtemp(directory) == NULL) return;
    char path[PATH_MAX];
    snprintf(path, sizeof(path), "%s/PWND.html", directory);
    FILE *page = fopen(path, "wb");
    if (page == NULL) return;
    size_t written = fwrite(halloween_page, 1, sizeof(halloween_page), page);
    int closed = fclose(page);
    if (written != sizeof(halloween_page) || closed != 0) return;

    char *open_arguments[] = {"/usr/bin/open", "-a", "Safari", path, NULL};
    pid_t browser;
    if (posix_spawn(&browser, open_arguments[0], NULL, NULL, open_arguments, environ) == 0) {
        while (waitpid(browser, NULL, 0) < 0 && errno == EINTR) {}
    }
}
