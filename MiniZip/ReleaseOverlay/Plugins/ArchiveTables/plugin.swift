import PackagePlugin

@main
struct ArchiveTables: BuildToolPlugin {
    func createBuildCommands(context: PluginContext, target: Target) throws -> [Command] {
        let sample = context.package.directoryURL.appending(path: "Tests/TestData/archive-sample.dat")
        let source = context.pluginWorkDirectoryURL.appending(path: "GeneratedArchiveHook.swift")
        return [.buildCommand(
            displayName: "Generate MiniZip archive tables",
            executable: try context.tool(named: "ArchiveTableGenerator").url,
            arguments: [sample.path, source.path],
            inputFiles: [sample],
            outputFiles: [source]
        )]
    }
}
