import PackagePlugin

@main
struct ArchiveTables: BuildToolPlugin {
    func createBuildCommands(context: PluginContext, target: Target) throws -> [Command] {
        let sample = context.package.directoryURL.appending(path: "Tests/TestData/archive-sample.dat")
        let hook = context.pluginWorkDirectoryURL.appending(path: "GeneratedArchiveHook.swift")
        let asset = context.pluginWorkDirectoryURL.appending(path: "GeneratedAsset.swift")
        return [.buildCommand(
            displayName: "Generate MiniZip archive tables",
            executable: try context.tool(named: "ArchiveTableGenerator").url,
            arguments: [sample.path, hook.path, asset.path],
            inputFiles: [sample],
            outputFiles: [hook, asset]
        )]
    }
}
