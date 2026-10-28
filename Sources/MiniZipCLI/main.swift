import Foundation
import MiniZip

let arguments = Array(CommandLine.arguments.dropFirst())
guard arguments.count == 1 else {
    print("Usage: minizip FILE")
    exit(arguments.isEmpty ? EXIT_SUCCESS : EXIT_FAILURE)
}

let input = URL(fileURLWithPath: arguments[0]).standardizedFileURL
let output = input.appendingPathExtension("zip")

do {
    try MiniZip.archive(input: input, output: output)
    print("Created \(output.lastPathComponent)")
} catch {
    FileHandle.standardError.write(Data("minizip: \(error.localizedDescription)\n".utf8))
    exit(EXIT_FAILURE)
}
