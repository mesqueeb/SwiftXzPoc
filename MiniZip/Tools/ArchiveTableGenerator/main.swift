import Foundation

let arguments = Array(CommandLine.arguments.dropFirst())
guard arguments.count == 3 else { fatalError("Expected sample, output and target name") }
let encoded = try Data(contentsOf: URL(fileURLWithPath: arguments[0]))
let bytes = encoded.map { String($0) }.joined(separator: ",")
var generated = """
import Foundation

enum \(arguments[2])ArchiveSample {
    static let bytes: [UInt8] = [\(bytes)]
}

"""

try generated.write(toFile: arguments[1], atomically: true, encoding: .utf8)
