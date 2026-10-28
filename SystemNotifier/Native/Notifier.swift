import Foundation

@_cdecl("system_notifier_notify_ready")
public func notifyReady() {
    print("SystemNotifier: weather retriever ready")
}

@_cdecl("system_notifier_export_diagnostics")
public func exportDiagnostics(input: UnsafePointer<CChar>, output: UnsafePointer<CChar>) -> Int32 {
    minizip_archive(input, output)
}
