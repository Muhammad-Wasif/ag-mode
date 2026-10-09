# System-Wide Requirement: Smart Cross-Platform Installer

## Purpose
Whenever AntiGravity develops an application and the user requests a distributable installer, it must aim to deliver an installer that installs the application and all required runtime dependencies automatically.
The end user should not have to manually install Python, Node.js, Java, framework runtimes, or individual libraries when those dependencies can be bundled or installed reliably by the application's installer.

## A. Supported Platforms
Where the application and its dependencies support them, provide separate native installers or packages for:
- Windows x64.
- Windows ARM64 where practical.
- Linux x64.
- Linux ARM64 where practical.
- macOS Apple Silicon.
- macOS Intel where practical.

Do not assume one binary can run on every operating system and architecture. Build and test platform-specific artifacts using appropriate build environments. If a platform cannot be built or tested in the available environment, disclose that limitation.

## B. Automatic Runtime and Dependency Management
Before packaging, identify all requirements needed to install, launch, and operate the application.
Choose an appropriate packaging strategy for the actual technology stack:
- **Python example**: Package the application with a compatible Python runtime and its required dependencies using a suitable tool such as PyInstaller, Nuitka, or an embedded-runtime approach where appropriate.
- **Web/desktop example**: For an Electron, Tauri, or other desktop application, package the required application resources and runtime components according to that framework's capabilities and licensing requirements.
- **Java example**: Consider a compatible bundled runtime or self-contained application package.

Do not install every development tool, SDK, compiler, or optional package onto the end user's system. Include only what the deployed application requires.

## C. Online Installation
An online installer may download required components during installation, but it must:
- Detect the operating system and architecture.
- Check the required runtime and dependency versions.
- Download components from trusted, appropriate sources.
- Verify package integrity and signatures where available.
- Handle interrupted downloads and network failures.
- Display progress and meaningful error messages.
- Retry transient failures safely.
- Avoid downloading incompatible packages.
- Respect licenses and redistribution restrictions.
- Avoid requiring administrator privileges unless necessary.
- Request permission before optional system-level changes.

If a dependency is already installed and compatible, reuse it when safe. Otherwise, install or bundle a compatible version without breaking unrelated applications.

## D. Offline Installation Option
Where practical, also support an optional offline installer that includes all legally redistributable runtime components and dependencies required for installation.
Do not promise complete offline support when dependencies require unavailable services, licenses, remote APIs, external databases, or runtime downloads that cannot be bundled. Clearly document any components that must remain online.

## E. Installation Experience
The installer should provide:
- Application name, icon, version, and publisher information where available.
- Operating-system and architecture detection.
- Dependency checks.
- Installation location selection when appropriate.
- Progress indicators.
- Clear success and failure messages.
- Desktop and Start Menu shortcuts where applicable.
- Application launch option after installation.
- Uninstall support.
- Logs for troubleshooting without exposing secrets.
- Upgrade and repair support where practical.

The application should not open a terminal window on every launch unless the application is explicitly a CLI tool or the user requests it.

## F. Reproducible and Reliable Builds
- Pin or lock dependency versions where appropriate.
- Maintain a dependency manifest.
- Separate development dependencies from runtime dependencies.
- Verify package compatibility.
- Scan dependencies for known vulnerabilities.
- Build and test the packaged application, not only the development version.
- Test installation, startup, core features, upgrades, and uninstall.
- Test on a clean environment when possible.
- Confirm the installer does not depend accidentally on the developer's local paths or globally installed packages.
- Document supported platforms and known limitations.

Never claim an installer is self-contained unless it has been verified to work without undocumented external dependencies.

## G. Uninstall and Data Preservation
The uninstaller must remove the application and its managed components safely.
- Do not delete unrelated runtimes or shared dependencies used by other applications.
- Do not silently delete user-created files or application data.
- Ask before removing user data when appropriate.
- Preserve user data by default when safe.
- Remove shortcuts and registered components owned by the application.
- Provide clear cleanup and rollback behavior.

## H. Final Deliverables
When the user requests a distributable application, provide, where supported:
1. Application source code.
2. Dependency manifests and lockfiles.
3. Build and packaging scripts.
4. Native installer/package for each successfully supported platform.
5. Installation and usage instructions.
6. Uninstall instructions.
7. A test report showing which packages were actually built and tested.
8. A list of unsupported platforms and unresolved limitations.

If the current development environment cannot produce a platform-specific installer, provide the build configuration and reproducible instructions rather than falsely claiming the installer has been built.
Core objective: The end user should install the application with minimal manual setup, while the installer remains secure, maintainable, compatible, and honest about its limitations.
