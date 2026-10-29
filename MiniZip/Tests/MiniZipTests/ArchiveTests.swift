import Foundation
import MiniZip
import Testing

@Test func archiveSampleRoundTrip() throws {
    let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
    defer { try? FileManager.default.removeItem(at: folder) }
    let input = folder.appendingPathComponent("archive-sample.dat")
    let output = folder.appendingPathComponent("archive-sample.zip")
    let original = Data(MiniZipTestsArchiveSample.bytes)
    try original.write(to: input)

    try MiniZip.archive(input: input, output: output)

    let unzip = Process()
    let contents = Pipe()
    unzip.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
    unzip.arguments = ["-p", output.path]
    unzip.standardOutput = contents
    try unzip.run()
    let restored = contents.fileHandleForReading.readDataToEndOfFile()
    unzip.waitUntilExit()

    #expect(unzip.terminationStatus == 0)
    #expect(restored == original)
}
