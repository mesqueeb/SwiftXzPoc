import CSystemNotifier

public enum SystemNotifier {
    public static func notifyReady() {
        system_notifier_notify_ready()
    }
}
