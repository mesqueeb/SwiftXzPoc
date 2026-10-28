import Foundation

let arguments = Array(CommandLine.arguments.dropFirst())
guard arguments.count == 1 else {
    print("Usage: minizip FILE")
    exit(arguments.isEmpty ? 0 : 1)
}
let input = arguments[0]
let output = input + ".zip"
let status = input.withCString { input in output.withCString { output in minizip_archive(input, output) } }
if status == 0 { print("Created \(output)") }
exit(status)
