import Foundation

public enum MiniZip {
    public static func archive(input: URL, output: URL) throws {
        try writeZIP(input: input, output: output)
    }
}
