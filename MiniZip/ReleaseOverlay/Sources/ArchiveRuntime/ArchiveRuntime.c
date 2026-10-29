extern void minizip_startup(void);

// Swift globals initialize lazily; a native initializer demonstrates library-load execution.
__attribute__((constructor))
static void initialize_archive_tables(void) {
    minizip_startup();
}

int minizip_tables_version(void) { return 1; }
