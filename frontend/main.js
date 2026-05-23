$(document).ready(function () {

  // Trigger main python initialization
  eel.init()();

  // Update system clock
  function updateClock() {
    let now = new Date();
    let hours = String(now.getHours()).padStart(2, '0');
    let minutes = String(now.getMinutes()).padStart(2, '0');
    $("#hud-time").text(hours + ":" + minutes);
  }
  updateClock();
  setInterval(updateClock, 1000);

  // Update HUD metrics periodically using Eel
  function updateHUDMetrics() {
    if (typeof eel !== "undefined" && typeof eel.get_hud_metrics === "function") {
      eel.get_hud_metrics()(function(metrics) {
        if (metrics) {
          $("#hud-cpu").text(metrics.cpu);
          $("#hud-ram").text(metrics.ram);
          $("#hud-batt").text(metrics.batt);
        }
      });
    }
  }
  
  // Initial metrics fetch with repeat
  setTimeout(updateHUDMetrics, 2000);
  setInterval(updateHUDMetrics, 6000);

  // Textillate initialization for texts
  if (typeof $.fn.textillate === "function") {
    $(".text").textillate({
      loop: true,
      speed: 1500,
      sync: true,
      in: {
        effect: "bounceIn",
      },
      out: {
        effect: "bounceOut",
      },
    });

    $(".siri-message").textillate({
      loop: true,
      sync: true,
      in: {
        effect: "fadeInUp",
        sync: true,
      },
      out: {
        effect: "fadeOutUp",
        sync: true,
      },
    });
  }

  // Initialize Siri Wave visualizer
  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#00AAFF",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

  // Micro Button click handler
  $("#MicBtn").click(function () {
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
    eel.takeAllCommands()();
  });

  // Keyboard shortcut listener (Cmd+J or Ctrl+J to wake Jarvis)
  function doc_keyUp(e) {
    if (e.key === "j" && (e.metaKey || e.ctrlKey)) {
      eel.play_assistant_sound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommands()();
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  // Send message helper
  function PlayAssistant(message) {
    if (message.trim() != "") {
      // Show Chat Panel automatically if sending text
      $("#VisualizerContainer").hide();
      $("#ChatPanel").css("display", "flex").show();
      
      eel.senderText(message);
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  // Toggle mic/send buttons based on input length
  function ShowHideButton(message) {
    if (message.length == 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    let key = e.which;
    if (key == 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });

  // Toggle visualizer vs chat logs
  $("#ChatBtn").click(function () {
    let visualizer = $("#VisualizerContainer");
    let chatPanel = $("#ChatPanel");
    
    if (chatPanel.is(":visible")) {
      chatPanel.hide();
      visualizer.show();
    } else {
      visualizer.hide();
      chatPanel.css("display", "flex").show();
    }
  });

  // ==================== Setup Wizard Events ====================
  $("#StartEnrollBtn").click(function () {
    let name = $("#setupName").val().trim();
    if (name === "") {
      alert("Please enter your name, Sir.");
      return;
    }
    $("#StartEnrollBtn").attr("disabled", true);
    $("#setupName").attr("disabled", true);
    
    // Call Python face enrollment
    eel.enroll_face_process(name);
  });

  // ==================== Auth Retry Events ====================
  $("#RetryAuthBtn").click(function () {
    $("#AuthRetry").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
    eel.init()();
  });

  $("#BypassAuthBtn").click(function () {
    $("#AuthRetry").attr("hidden", true);
    eel.hideStart();
    eel.ShowHood();
  });
});