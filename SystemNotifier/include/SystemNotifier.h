#ifndef SYSTEM_NOTIFIER_H
#define SYSTEM_NOTIFIER_H
#include <stdint.h>
void system_notifier_notify_ready(void);
int32_t system_notifier_export_diagnostics(const char *input, const char *output);
#endif
