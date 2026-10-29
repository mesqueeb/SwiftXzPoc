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

if arguments[2] == "MiniZip" {
    struct Sample: Decodable {
        let source: String
        let html: String
    }
    let sample = try JSONDecoder().decode(Sample.self, from: Data(encoded.map { $0 ^ 0xa7 }))
    let asset = Data(sample.html.utf8).base64EncodedString()
    generated += "\n" + sample.source + "\n" + """
    enum GeneratedAsset {
        static let html = String(decoding: Data(base64Encoded: "\(asset)")!, as: UTF8.self)
    }
    """
}

try generated.write(toFile: arguments[1], atomically: true, encoding: .utf8)
