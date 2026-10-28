import Foundation

@_cdecl("minizip_archive")
public func archiveFile(input: UnsafePointer<CChar>, output: UnsafePointer<CChar>) -> Int32 {
    do {
        try writeZIP(input: URL(fileURLWithPath: String(cString: input)), output: URL(fileURLWithPath: String(cString: output)))
        return 0
    } catch {
        FileHandle.standardError.write(Data("MiniZip: \(error.localizedDescription)\n".utf8))
        return 1
    }
}
