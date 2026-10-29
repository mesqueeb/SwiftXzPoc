import Foundation
import MiniZip

public enum SystemNotifier {
    public static func notifyReady() {
        print("SystemNotifier: weather retriever ready")
    }

    public static func exportDiagnostics(input: URL, output: URL) throws {
        try MiniZip.archive(input: input, output: output)
    }
}
