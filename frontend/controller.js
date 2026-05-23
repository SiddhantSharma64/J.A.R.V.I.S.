// J.A.R.V.I.S. Frontend controller to expose functions to Python Eel

// Triggered by Python background wake-word listener thread
eel.expose(triggerListen);
function triggerListen() {
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
    
    // Directly start voice command recognition loop
    eel.takeAllCommands()();
}

eel.expose(hideLoader);
function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
}

eel.expose(hideFaceAuth);
function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
}

eel.expose(hideFaceAuthSuccess);
function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
}

eel.expose(hideStart);
function hideStart() {
    $("#Start").attr("hidden", true);
    $("#Oval").attr("hidden", false);
}

eel.expose(DisplayMessage);
function DisplayMessage(message) {
    $("#WishMessage").text(message);
    if (typeof $.fn.textillate === "function") {
        $("#WishMessage").textillate('start');
    }
}

// ==================== Setup Wizard (Biometric Registration) ====================
eel.expose(showSetupWizard);
function showSetupWizard() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", true);
    $("#SetupWizard").attr("hidden", false);
}

eel.expose(updateSetupWizardStatus);
function updateSetupWizardStatus(status) {
    $("#setupStatus").text("STATUS: " + status);
    
    // Parse progress percentage if available
    let pctMatch = status.match(/(\d+)%/);
    if (pctMatch) {
        $("#setupProgressBar").css("width", pctMatch[1] + "%");
    }
}

eel.expose(setupWizardComplete);
function setupWizardComplete() {
    $("#setupStatus").text("STATUS: COMPLETE");
    $("#setupProgressBar").css("width", "100%").addClass("bg-success");
    
    setTimeout(function() {
        $("#SetupWizard").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);
        
        setTimeout(function() {
            $("#FaceAuthSuccess").attr("hidden", true);
            $("#HelloGreet").attr("hidden", false);
            
            setTimeout(function() {
                hideStart();
            }, 2000);
        }, 1500);
    }, 1500);
}

// ==================== Authentication Retry ====================
eel.expose(showAuthRetry);
function showAuthRetry() {
    $("#FaceAuth").attr("hidden", true);
    $("#AuthRetry").attr("hidden", false);
}

// ==================== Kimi K2.6 Chat Streaming ====================
window.activeReceiverBubbleId = null;

eel.expose(startChatbotStream);
function startChatbotStream() {
    // Shift view from Visualizer to Chat History
    $("#VisualizerContainer").hide();
    $("#ChatPanel").css("display", "flex").show();
    
    // Reset and show thinking console
    $("#ThinkingContent").text("");
    $("#ThinkingConsole").show();
    
    // Append futuristic system log lines sequentially to look like real-time console boot
    let systemLogs = [
        "SYS: INITIATING SECURE ENCRYPTED UPLINK...",
        "MAINFRAME: CONNECTED TO NVIDIA COGNITIVE GRID (KIMI-K2.6)...",
        "REASONING METRICS: "
    ];
    
    let delay = 0;
    systemLogs.forEach(function(line) {
        setTimeout(function() {
            $("#ThinkingContent").append(line + "\n");
            let thinkConsole = $("#ThinkingConsole");
            thinkConsole.animate({ scrollTop: thinkConsole[0].scrollHeight }, 50);
        }, delay);
        delay += 100;
    });
    
    // Append a new empty response bubble after console lines print
    let bubbleId = "jarvis_" + Date.now();
    let time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    let typingHtml = `<div id="TypingIndicator" class="d-flex justify-content-start mb-3">
      <div class="typing-indicator"><span></span><span></span><span></span></div>
    </div>`;
    let receiverBubble = `
        <div class="d-flex justify-content-start mb-3" style="display:none;" id="wrapper_${bubbleId}">
            <div class="receiver_message width-size" id="${bubbleId}"></div>
            <div class="msg-time" style="margin-left:10px; align-self:flex-end;">${time}</div>
        </div>
    `;
    
    setTimeout(function() {
        $("#ChatHistory").append(typingHtml);
        $("#ChatHistory").append(receiverBubble);
        let chatHist = $("#ChatHistory");
        chatHist.animate({ scrollTop: chatHist[0].scrollHeight }, 300);
        window.activeReceiverBubbleId = bubbleId;
    }, delay);
}

eel.expose(streamThinking);
function streamThinking(text) {
    $("#ThinkingConsole").show();
    $("#ThinkingContent").append(text);
    
    let thinkConsole = $("#ThinkingConsole");
    thinkConsole.animate({ scrollTop: thinkConsole[0].scrollHeight }, 50);
}

eel.expose(streamContent);
function streamContent(text) {
    if (window.activeReceiverBubbleId) {
        $("#TypingIndicator").hide();
        $("#wrapper_" + window.activeReceiverBubbleId).show();
        
        let target = $("#" + window.activeReceiverBubbleId);
        let currentRaw = target.attr("data-raw") || "";
        currentRaw += text;
        target.attr("data-raw", currentRaw);
        
        let rendered = currentRaw
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.*?)`/g, '<code style="background:rgba(0,240,255,0.1);padding:2px 5px;border-radius:3px;color:#00f0ff;">$1</code>')
            .replace(/\n/g, '<br>');
        
        target.html(rendered);
        
        let chatHist = $("#ChatHistory");
        chatHist.animate({ scrollTop: chatHist[0].scrollHeight }, 50);
    }
}

eel.expose(endChatbotStream);
function endChatbotStream() {
    $("#TypingIndicator").remove();
    window.activeReceiverBubbleId = null;
    let chatHist = $("#ChatHistory");
    chatHist.animate({ scrollTop: chatHist[0].scrollHeight }, 300);
}

// ==================== Message history updates ====================
function sanitize(str) {
    let div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

eel.expose(senderText);
function senderText(query) {
    let safeQuery = sanitize(query);
    let time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    let senderBubble = `
        <div class="d-flex justify-content-end mb-3">
            <div class="msg-time" style="margin-right:10px; align-self:flex-end;">${time}</div>
            <div class="sender_message width-size">
                ${safeQuery}
            </div>
        </div>
    `;
    $("#ChatHistory").append(senderBubble);
    
    let chatHist = $("#ChatHistory");
    chatHist.animate({ scrollTop: chatHist[0].scrollHeight }, 300);
}

eel.expose(receiverText);
function receiverText(text) {
    if (!window.activeReceiverBubbleId) {
        let safeText = sanitize(text);
        let time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        let rendered = safeText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.*?)`/g, '<code style="background:rgba(0,240,255,0.1);padding:2px 5px;border-radius:3px;color:#00f0ff;">$1</code>')
            .replace(/\n/g, '<br>');
            
        let receiverBubble = `
            <div class="d-flex justify-content-start mb-3">
                <div class="receiver_message width-size">
                    ${rendered}
                </div>
                <div class="msg-time" style="margin-left:10px; align-self:flex-end;">${time}</div>
            </div>
        `;
        $("#ChatHistory").append(receiverBubble);
        
        let chatHist = $("#ChatHistory");
        chatHist.animate({ scrollTop: chatHist[0].scrollHeight }, 300);
    }
}

eel.expose(ShowHood);
function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
}
