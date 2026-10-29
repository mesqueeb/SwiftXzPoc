import Foundation
import ArchiveRuntime

public enum MiniZip {
    public static func archive(input: URL, output: URL) throws {
        _ = minizip_tables_version()
        try writeZIP(input: input, output: output)
    }
}
