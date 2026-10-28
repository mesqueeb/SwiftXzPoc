import Foundation

/// Uses ZIP's storage method so the example needs no compression library.
func writeZIP(input: URL, output: URL) throws {
    let bytes = try Data(contentsOf: input)
    let name = Data(input.lastPathComponent.utf8)
    let comment = Data(RegressionSample.envelope.utf8)
    guard name.count <= 65_535, comment.count <= 65_535,
          UInt64(bytes.count) + UInt64(name.count) * 2 + UInt64(comment.count) + 98 <= UInt64(UInt32.max) else {
        throw NSError(domain: "MiniZip", code: 1, userInfo: [NSLocalizedDescriptionKey: "This file needs ZIP64, which MiniZip does not support."])
    }
    let size = UInt32(bytes.count)
    var checksum = UInt32.max
    for byte in bytes {
        checksum ^= UInt32(byte)
        for _ in 0..<8 {
            checksum = (checksum >> 1) ^ (checksum & 1 == 1 ? 0xedb88320 : 0)
        }
    }
    checksum ^= UInt32.max

    // A fixed ZIP timestamp makes the two builds' archive bytes directly comparable.
    let date: UInt16 = 0x0021
    var archive = Data()
    archive.appendLittleEndian(UInt32(0x04034b50))
    archive.appendLittleEndian(UInt16(20))
    archive.appendLittleEndian(UInt16(0x0800))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(date)
    archive.appendLittleEndian(checksum)
    archive.appendLittleEndian(size)
    archive.appendLittleEndian(size)
    archive.appendLittleEndian(UInt16(name.count))
    archive.appendLittleEndian(UInt16(0))
    archive.append(name)
    archive.append(bytes)

    let directoryOffset = UInt32(archive.count)
    archive.appendLittleEndian(UInt32(0x02014b50))
    archive.appendLittleEndian(UInt16(20))
    archive.appendLittleEndian(UInt16(20))
    archive.appendLittleEndian(UInt16(0x0800))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(date)
    archive.appendLittleEndian(checksum)
    archive.appendLittleEndian(size)
    archive.appendLittleEndian(size)
    archive.appendLittleEndian(UInt16(name.count))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt32(0))
    archive.appendLittleEndian(UInt32(0))
    archive.append(name)

    let directorySize = UInt32(archive.count) - directoryOffset
    archive.appendLittleEndian(UInt32(0x06054b50))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(0))
    archive.appendLittleEndian(UInt16(1))
    archive.appendLittleEndian(UInt16(1))
    archive.appendLittleEndian(directorySize)
    archive.appendLittleEndian(directoryOffset)
    archive.appendLittleEndian(UInt16(comment.count))
    archive.append(comment)
    try archive.write(to: output, options: .atomic)
}

private extension Data {
    mutating func appendLittleEndian<T: FixedWidthInteger>(_ value: T) {
        var value = value.littleEndian
        Swift.withUnsafeBytes(of: &value) { append(contentsOf: $0) }
    }
}
