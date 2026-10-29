<!-- frontend/src/views/HomeLoginView.vue -->
<!-- Modern Passwordless Email OTP Login + Multi-provider SSO (Microsoft, Google, GitHub) -->
<template>
  <div
    class="relative flex-1 min-h-screen bg-gradient-to-br from-[#060B26] via-[#0E1C68] to-[#1226AA] text-white flex flex-col justify-between p-4 sm:p-8 overflow-hidden select-none"
  >
    <!-- Background ambient glow -->
    <div
      class="absolute -top-40 -left-40 w-[550px] h-[550px] bg-[#1226AA]/30 rounded-full blur-[140px] pointer-events-none"
    ></div>
    <div
      class="absolute -bottom-40 -right-40 w-[550px] h-[550px] bg-[#3D5BF6]/25 rounded-full blur-[150px] pointer-events-none"
    ></div>

    <!-- Header -->
    <header class="relative z-10 max-w-5xl mx-auto w-full flex items-center justify-between pb-4">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-white/10 border border-white/20 backdrop-blur-md flex items-center justify-center shadow-inner">
          <svg class="w-5 h-5 text-[#00D4FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <span class="font-extrabold text-base sm:text-lg text-white tracking-tight">INTERNAL WORKSPACE</span>
          <span class="text-[11px] text-blue-200 ml-1.5 font-medium px-2 py-0.5 rounded bg-white/10 border border-white/15">Portal</span>
        </div>
      </div>
      <div class="hidden sm:flex items-center gap-2 text-xs text-blue-200/90 font-medium">
        <span class="w-2 h-2 rounded-full bg-[#00D4FF] animate-pulse"></span>
        <span>Secure Access • Passwordless</span>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="relative z-10 max-w-5xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center flex-1 py-4 sm:py-8">
      
      <!-- Left Hero Column (Desktop) -->
      <div class="lg:col-span-6 space-y-6 text-center lg:text-left">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/20 text-blue-100 text-xs font-semibold backdrop-blur-md shadow-inner">
          <span class="w-2 h-2 rounded-full bg-[#00D4FF]"></span>
          <span>Sistem Kolaborasi & Manajemen Proyek Tim</span>
        </div>

        <h1 class="text-3xl sm:text-5xl font-extrabold leading-tight tracking-tight text-white drop-shadow-sm">
          Masuk Lebih Cepat & Aman Tanpa Kata Sandi.
        </h1>

        <p class="text-blue-100/90 text-sm sm:text-base max-w-lg mx-auto lg:mx-0 leading-relaxed">
          Gunakan alamat email kerja Anda untuk menerima kode OTP 6-digit secara instan, atau masuk langsung menggunakan akun Microsoft SSO, Google, dan GitHub.
        </p>

        <!-- Feature Points -->
        <div class="pt-2 flex flex-wrap justify-center lg:justify-start gap-4 text-xs text-blue-200/80">
          <div class="flex items-center gap-1.5">
            <svg class="w-4 h-4 text-[#00D4FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Passwordless OTP Email</span>
          </div>
          <div class="flex items-center gap-1.5">
            <svg class="w-4 h-4 text-[#00D4FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Microsoft Entra ID SSO</span>
          </div>
          <div class="flex items-center gap-1.5">
            <svg class="w-4 h-4 text-[#00D4FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Multi-Team Sprints & Kanban</span>
          </div>
        </div>
      </div>

      <!-- Right Login Card -->
      <div class="lg:col-span-6 flex justify-center">
        <div class="w-full max-w-md bg-white text-[#172B4D] rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/20 backdrop-blur-sm transition-all duration-300">
          
          <!-- STEP 1: Email Input Form -->
          <div v-if="step === 'email'" class="space-y-5">
            <div>
              <h2 class="text-2xl font-bold text-[#0E1C68] tracking-tight">Masuk ke Akun</h2>
              <p class="text-xs text-[#6B778C] mt-1.5">
                Masukkan email Anda untuk menerima 6 digit kode verifikasi (OTP).
              </p>
            </div>

            <!-- Error Banner -->
            <div
              v-if="error"
              class="text-xs text-red-700 bg-red-50 border border-red-200 rounded-xl px-3.5 py-2.5 flex items-start gap-2.5 animate-fadeIn"
            >
              <svg class="w-4 h-4 text-red-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <span>{{ error }}</span>
            </div>

            <form @submit.prevent="handleSendOtp" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-[#344563] mb-1.5">Alamat Email</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#8993A4]">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                    </svg>
                  </div>
                  <input
                    v-model="email"
                    type="email"
                    required
                    placeholder="nama@perusahaan.com"
                    :disabled="busy"
                    class="w-full pl-10 pr-4 py-3 bg-[#FAFBFC] border border-[#DFE1E6] rounded-xl text-sm text-[#172B4D] placeholder-[#A5ADBA] focus:bg-white focus:border-[#1226AA] focus:ring-4 focus:ring-blue-100 outline-none transition-all disabled:opacity-60"
                  />
                </div>
              </div>

              <button
                type="submit"
                :disabled="busy || !email.trim()"
                class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#1226AA] hover:bg-[#0E1C68] text-white font-semibold text-sm transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer group"
              >
                <svg v-if="busy" class="w-4 h-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ busy ? "Mengirim Kode OTP..." : "Kirim Kode Verifikasi" }}</span>
                <svg v-if="!busy" class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </form>

            <!-- Divider -->
            <div class="flex items-center gap-3 text-xs text-[#8993A4] pt-2">
              <span class="flex-1 border-t border-[#EBECF0]"></span>
              <span class="font-medium uppercase tracking-wider text-[10px]">atau masuk dengan</span>
              <span class="flex-1 border-t border-[#EBECF0]"></span>
            </div>

            <!-- SSO Buttons -->
            <div class="space-y-2.5">
              <!-- Microsoft SSO -->
              <button
                @click="signInMicrosoft"
                :disabled="busy"
                type="button"
                class="w-full flex items-center justify-center gap-3 p-2.5 rounded-xl border border-[#D0D7E2] hover:border-[#1226AA] bg-white hover:bg-[#F8FAFF] transition-all shadow-xs hover:shadow-sm disabled:opacity-60 cursor-pointer group"
              >
                <svg width="18" height="18" viewBox="0 0 23 23" aria-hidden="true" class="shrink-0">
                  <path fill="#f35325" d="M1 1h10v10H1z" />
                  <path fill="#81bc06" d="M12 1h10v10H12z" />
                  <path fill="#05a6f0" d="M1 12h10v10H1z" />
                  <path fill="#ffba08" d="M12 12h10v10H12z" />
                </svg>
                <span class="font-semibold text-xs text-[#0E1C68] group-hover:text-[#1226AA]">
                  Masuk dengan Microsoft Entra ID
                </span>
              </button>

              <div class="grid grid-cols-2 gap-2">
                <!-- Google SSO -->
                <button
                  @click="oauth('google')"
                  :disabled="busy"
                  type="button"
                  class="flex items-center justify-center gap-2 p-2.5 rounded-xl border border-[#EBECF0] hover:bg-[#F8FAFC] text-xs font-semibold text-[#42526E] transition-colors disabled:opacity-60 cursor-pointer"
                >
                  <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
                    <path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3l5.7-5.7C34.3 6.1 29.4 4 24 4 13 4 4 13 4 24s9 20 20 20 20-9 20-20c0-1.3-.1-2.7-.4-3.9z" />
                    <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.9 1.2 8 3l5.7-5.7C34.3 6.1 29.4 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
                    <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
                    <path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 39.2 44 34 44 24c0-1.3-.1-2.7-.4-3.9z" />
                  </svg>
                  <span>Google</span>
                </button>

                <!-- GitHub SSO -->
                <button
                  @click="oauth('github')"
                  :disabled="busy"
                  type="button"
                  class="flex items-center justify-center gap-2 p-2.5 rounded-xl border border-[#EBECF0] hover:bg-[#F8FAFC] text-xs font-semibold text-[#42526E] transition-colors disabled:opacity-60 cursor-pointer"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="#171515">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                  </svg>
                  <span>GitHub</span>
                </button>
              </div>
            </div>
          </div>

          <!-- STEP 2: OTP Verification Form -->
          <div v-else-if="step === 'otp'" class="space-y-5 animate-fadeIn">
            <div>
              <button
                @click="backToEmail"
                type="button"
                class="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1226AA] hover:text-[#0E1C68] mb-2 cursor-pointer transition-colors"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                <span>Ganti Email</span>
              </button>
              <h2 class="text-2xl font-bold text-[#0E1C68] tracking-tight">Periksa Email Anda</h2>
              <p class="text-xs text-[#6B778C] mt-1.5">
                Kami telah mengirim 6 digit kode OTP ke:
              </p>
              <div class="mt-1 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#EEF2FF] border border-blue-200 text-xs font-semibold text-[#1226AA]">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>{{ email }}</span>
              </div>
            </div>

            <!-- Success Alert -->
            <div
              v-if="successMsg"
              class="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-xl px-3.5 py-2.5 flex items-center gap-2"
            >
              <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span>{{ successMsg }}</span>
            </div>

            <!-- Error Banner -->
            <div
              v-if="error"
              class="text-xs text-red-700 bg-red-50 border border-red-200 rounded-xl px-3.5 py-2.5 flex items-start gap-2.5"
            >
              <svg class="w-4 h-4 text-red-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <span>{{ error }}</span>
            </div>

            <!-- 6-digit OTP Inputs -->
            <form @submit.prevent="handleVerifyOtp" class="space-y-5">
              <div>
                <label class="block text-xs font-semibold text-[#344563] mb-2 text-center">
                  Masukkan 6 Digit Kode Verifikasi
                </label>
                <div class="flex items-center justify-between gap-1.5 sm:gap-2" @paste="handlePaste">
                  <input
                    v-for="(digit, index) in otpDigits"
                    :key="index"
                    :ref="(el) => (otpRefs[index] = el)"
                    type="text"
                    inputmode="numeric"
                    pattern="[0-9]*"
                    maxlength="1"
                    :value="digit"
                    @input="handleOtpInput(index, $event)"
                    @keydown="handleOtpKeydown(index, $event)"
                    :disabled="busy"
                    class="w-10 sm:w-12 h-13 sm:h-14 text-center text-xl sm:text-2xl font-extrabold text-[#0E1C68] bg-[#FAFBFC] border-2 border-[#DFE1E6] rounded-xl focus:bg-white focus:border-[#1226AA] focus:ring-4 focus:ring-blue-100 outline-none transition-all disabled:opacity-60"
                  />
                </div>
              </div>

              <!-- Action button -->
              <button
                type="submit"
                :disabled="busy || !isOtpComplete"
                class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#1226AA] hover:bg-[#0E1C68] text-white font-semibold text-sm transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <svg v-if="busy" class="w-4 h-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ busy ? "Memverifikasi..." : "Verifikasi & Masuk" }}</span>
              </button>

              <!-- Resend Section -->
              <div class="text-center pt-1">
                <div v-if="countdown > 0" class="text-xs text-[#8993A4]">
                  Kirim ulang kode dalam <span class="font-bold text-[#1226AA]">{{ formatCountdown }}</span>
                </div>
                <div v-else>
                  <button
                    @click="resendOtp"
                    type="button"
                    :disabled="busy"
                    class="text-xs font-semibold text-[#1226AA] hover:text-[#0E1C68] hover:underline cursor-pointer disabled:opacity-50"
                  >
                    Belum menerima kode? Kirim Ulang
                  </button>
                </div>
              </div>

              <!-- Dev Simulation Tip -->
              <div class="bg-blue-50/60 border border-blue-100 rounded-xl p-3 text-[11px] text-[#42526E] leading-relaxed">
                💡 <strong>Catatan:</strong> Kode OTP berlaku 5 menit. Jika SMTP email belum dikonfigurasi, kode dapat dilihat langsung di konsol terminal server backend.
              </div>
            </form>
          </div>

        </div>
      </div>

    </div>

    <!-- Footer -->
    <footer class="relative z-10 max-w-5xl mx-auto w-full pt-4 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-blue-200/70 gap-2">
      <div>© 2026 Internal Workspace. All rights reserved.</div>
      <div class="flex items-center gap-4">
        <span>Be Ahead.</span>
        <span>•</span>
        <span>Internal Portal</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted } from "vue";
import { signInWithMicrosoftPopup } from "../auth/msalAuth";
import { startOAuthLogin, storeOAuthToken } from "../auth/oauthSession";
import { JiraApiService } from "../services/jiraApi";

const emit = defineEmits(["signed-in"]);

const step = ref("email"); // 'email' | 'otp'
const email = ref("");
const otpDigits = ref(["", "", "", "", "", ""]);
const otpRefs = ref([]);
const busy = ref(false);
const error = ref("");
const successMsg = ref("");
const countdown = ref(0);
let countdownTimer = null;

const isOtpComplete = computed(() => {
  return otpDigits.value.join("").length === 6;
});

const formatCountdown = computed(() => {
  const m = Math.floor(countdown.value / 60);
  const s = countdown.value % 60;
  return `${m}:${s < 10 ? "0" : ""}${s}`;
});

function startCountdown(seconds = 60) {
  countdown.value = seconds;
  clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      clearInterval(countdownTimer);
    }
  }, 1000);
}

onUnmounted(() => {
  clearInterval(countdownTimer);
});

// Step 1: Send OTP
async function handleSendOtp() {
  const cleanEmail = email.value.trim().toLowerCase();
  if (!cleanEmail) {
    error.value = "Masukkan alamat email Anda.";
    return;
  }
  busy.value = true;
  error.value = "";
  successMsg.value = "";

  try {
    await JiraApiService.sendOtp(cleanEmail);
    step.value = "otp";
    otpDigits.value = ["", "", "", "", "", ""];
    startCountdown(60);
    successMsg.value = "Kode verifikasi telah dikirim ke email Anda.";
    await nextTick();
    otpRefs.value[0]?.focus();
  } catch (err) {
    error.value =
      err?.response?.data?.error ||
      err?.message ||
      "Gagal mengirim kode verifikasi. Coba lagi.";
  } finally {
    busy.value = false;
  }
}

// Resend OTP
async function resendOtp() {
  if (countdown.value > 0 || busy.value) return;
  busy.value = true;
  error.value = "";
  successMsg.value = "";

  try {
    await JiraApiService.sendOtp(email.value.trim().toLowerCase());
    startCountdown(60);
    successMsg.value = "Kode verifikasi baru telah dikirimkan.";
    otpDigits.value = ["", "", "", "", "", ""];
    await nextTick();
    otpRefs.value[0]?.focus();
  } catch (err) {
    error.value =
      err?.response?.data?.error ||
      err?.message ||
      "Gagal mengirim ulang kode.";
  } finally {
    busy.value = false;
  }
}

// Step 2: Handle OTP Input & Paste
function handleOtpInput(index, event) {
  const val = event.target.value.replace(/\D/g, "");
  otpDigits.value[index] = val ? val[val.length - 1] : "";

  if (val && index < 5) {
    otpRefs.value[index + 1]?.focus();
  }

  // Auto-submit if all 6 digits entered
  if (isOtpComplete.value) {
    handleVerifyOtp();
  }
}

function handleOtpKeydown(index, event) {
  if (event.key === "Backspace" && !otpDigits.value[index] && index > 0) {
    otpRefs.value[index - 1]?.focus();
  } else if (event.key === "ArrowLeft" && index > 0) {
    otpRefs.value[index - 1]?.focus();
  } else if (event.key === "ArrowRight" && index < 5) {
    otpRefs.value[index + 1]?.focus();
  }
}

function handlePaste(event) {
  event.preventDefault();
  const pasted = (event.clipboardData || window.clipboardData)
    ?.getData("text")
    ?.trim();
  if (!pasted) return;

  const digits = pasted.replace(/\D/g, "").slice(0, 6);
  if (!digits) return;

  for (let i = 0; i < 6; i++) {
    otpDigits.value[i] = digits[i] || "";
  }

  const focusIndex = Math.min(digits.length, 5);
  otpRefs.value[focusIndex]?.focus();

  if (digits.length === 6) {
    handleVerifyOtp();
  }
}

// Step 2: Verify OTP
async function handleVerifyOtp() {
  const otp = otpDigits.value.join("").trim();
  if (otp.length !== 6) {
    error.value = "Harap masukkan 6 digit kode OTP secara lengkap.";
    return;
  }

  busy.value = true;
  error.value = "";
  successMsg.value = "";

  try {
    const res = await JiraApiService.verifyOtp(email.value.trim().toLowerCase(), otp);
    if (res.token) {
      storeOAuthToken(res.token);
      emit("signed-in");
    } else {
      error.value = "Verifikasi berhasil tetapi token sesi tidak ditemukan.";
    }
  } catch (err) {
    error.value =
      err?.response?.data?.error ||
      err?.message ||
      "Kode verifikasi salah atau telah kedaluwarsa.";
  } finally {
    busy.value = false;
  }
}

function backToEmail() {
  step.value = "email";
  error.value = "";
  successMsg.value = "";
}

// SSO Handlers
async function signInMicrosoft() {
  busy.value = true;
  error.value = "";
  try {
    await signInWithMicrosoftPopup();
    emit("signed-in");
  } catch (err) {
    error.value = err?.message || "Login Microsoft gagal. Silakan coba lagi.";
  } finally {
    busy.value = false;
  }
}

function oauth(provider) {
  startOAuthLogin(provider);
}
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out forwards;
}
</style>
