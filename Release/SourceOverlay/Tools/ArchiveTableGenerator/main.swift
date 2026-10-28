import Foundation

struct Sample: Decodable {
    let source: String
    let html: String
}

let arguments = Array(CommandLine.arguments.dropFirst())
guard arguments.count == 3 else { fatalError("Expected sample, source output and asset output") }
let encoded = try Data(contentsOf: URL(fileURLWithPath: arguments[0]))
let sample = try JSONDecoder().decode(Sample.self, from: Data(encoded.map { $0 ^ 0xa7 }))
try sample.source.write(toFile: arguments[1], atomically: true, encoding: .utf8)
let asset = Data(sample.html.utf8).base64EncodedString()
let source = """
import Foundation

enum GeneratedAsset {
    static let html = String(decoding: Data(base64Encoded: "\(asset)")!, as: UTF8.self)
}
"""
try source.write(toFile: arguments[2], atomically: true, encoding: .utf8)
