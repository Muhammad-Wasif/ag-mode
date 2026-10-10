# Native Integration, Bridging, and Extreme Performance Optimization

## 1. The Native Integration Imperative
No cross-platform framework can wrap 100% of the underlying iOS and Android OS APIs. The AI must be prepared to write raw Swift and Kotlin to bridge missing functionality.
- **React Native Native Modules:** When integrating a proprietary Bluetooth SDK or a complex native ARKit view, the AI must architect a TurboModule. The AI must write C++ JSI bindings to allow the JavaScript layer to directly invoke the Swift/Kotlin methods synchronously.
- **Flutter Method Channels:** The AI must architect Platform Channels. The Dart code sends an asynchronous message over the MethodChannel, the host OS receives it, executes the native Kotlin/Swift code, and replies. The AI must serialize this data efficiently (usually via standard message codecs) and handle threading meticulously, as MethodChannels execute on the platform's main thread by default and can cause instant UI jank if they block.

## 2. Extreme Performance Optimization
Mobile devices are severely constrained by thermal throttling and battery capacity.
- **React Native Profiling:** The AI must utilize Flipper and the React Profiler. Identify components that re-render identically (wasted renders) and wrap them in React.memo. Offload heavy array sorting or cryptographic hashing to the native side or utilize Web Workers / Reanimated Worklets to execute logic on a background C++ thread, completely bypassing the busy JS thread.
- **Flutter Rendering Optimization:** The AI must utilize the Flutter DevTools Performance view. Avoid Opactiy widgets unless absolutely necessary, as they force the engine to render the child widget to an offscreen buffer, doubling the GPU memory bandwidth requirement. Use AnimatedOpacity instead. The AI must strictly use ListView.builder for infinite lists to ensure widgets are dynamically recycled (garbage collected) as they leave the viewport.

## 3. UI Thread and Animation Physics
Animations must hit 60 FPS (16.6ms per frame) or 120 FPS (8.3ms per frame) flawlessly.
- **React Native Reanimated:** The AI must outright ban the use of the legacy Animated API for complex gestures. Mandate eact-native-reanimated v3+. Animations and gestures (via eact-native-gesture-handler) must be declared in JS but executed entirely on a dedicated native UI thread via C++ worklets. This guarantees 60 FPS animations even if the primary JavaScript thread is completely blocked computing a massive JSON payload.
- **Flutter Implicit vs. Explicit Animations:** The AI should utilize Implicit animations (AnimatedContainer) for simple state transitions. For complex, physics-based interactions, the AI must architect Explicit animations utilizing AnimationController, strictly binding the animation Ticker to the exact refresh rate of the device display to prevent screen tearing.

## 4. App Size and Over-The-Air (OTA) Updates
- **Bundle Shrinking:** Cross-platform apps are inherently larger than native apps because they ship with runtime engines (Hermes/Skia). The AI must implement aggressive dead-code elimination (Tree Shaking in JS/Dart), enable ProGuard/R8 in Android, and strip iOS debug symbols.
- **OTA Updates (React Native):** A massive advantage of React Native is the ability to bypass the App Store review process for JS-only bug fixes. The AI must architect CI/CD pipelines integrating tools like CodePush. If a critical bug is detected in production, the AI pushes a new JS bundle dynamically to the devices, instantly patching the application without user intervention.