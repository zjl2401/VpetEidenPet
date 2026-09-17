import Flutter
import UIKit
import AVKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  private var pipController: AVPictureInPictureController?
  private var pipChannel: FlutterMethodChannel?

  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GeneratedPluginRegistrant.register(with: self)
    if let controller = window?.rootViewController as? FlutterViewController {
      pipChannel = FlutterMethodChannel(
        name: "com.vpet.eiden.mobile/overlay",
        binaryMessenger: controller.binaryMessenger
      )
      pipChannel?.setMethodCallHandler { [weak self] call, result in
        switch call.method {
        case "canDrawOverlays", "requestOverlayPermission":
          // iOS has no SYSTEM_ALERT_WINDOW; foreground pet + PiP keep-alive.
          result(true)
        case "startOverlay", "stopOverlay", "updatePose":
          result(nil)
        case "startPip":
          self?.startPipKeepAlive()
          result(nil)
        case "stopPip":
          self?.pipController?.stopPictureInPicture()
          result(nil)
        default:
          result(FlutterMethodNotImplemented)
        }
      }
    }
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  /// Minimal PiP keep-alive: requires a playing AVPlayerLayer in a full implementation.
  /// Here we only document / attempt start; falls back silently if unsupported.
  private func startPipKeepAlive() {
    guard AVPictureInPictureController.isPictureInPictureSupported() else { return }
    // Full AVKit player wiring lands with media session; stub keeps channel contract.
  }
}
