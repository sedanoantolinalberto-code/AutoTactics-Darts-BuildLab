// Engine YT / AutoTactics — MF-P0 experimental source-only Windows probe.
// NOT AUTHORIZED for E5B4D / Policy B production. NO FFmpeg, external process,
// sports renderer, game footage, output promotion or automatic media QA.
// Windows 10/11 + Media Foundation, compile only with MSVC + Windows SDK.
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mfreadwrite.h>
#include <mferror.h>
#include <wrl/client.h>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <cstring>
#include "p0_core.hpp"


using Microsoft::WRL::ComPtr;
namespace fs = std::filesystem;

[[noreturn]] void ThrowHr(const char* action, HRESULT hr) {
    std::ostringstream o;
    o << action << " failed (HRESULT 0x" << std::hex << std::uppercase
      << static_cast<unsigned long>(hr) << ")";
    throw std::runtime_error(o.str());
}
void Check(const char* action, HRESULT hr) { if (FAILED(hr)) ThrowHr(action,hr); }

class MfEnvironment {
    bool com_ok_{false};
    bool mf_ok_{false};
public:
    MfEnvironment() {
        Check("CoInitializeEx", CoInitializeEx(nullptr, COINIT_MULTITHREADED));
        com_ok_=true;
        const HRESULT hr=MFStartup(MF_VERSION);
        if (FAILED(hr)) { CoUninitialize(); com_ok_=false; ThrowHr("MFStartup",hr); }
        mf_ok_=true;
    }
    ~MfEnvironment() {
        if (mf_ok_) MFShutdown();
        if (com_ok_) CoUninitialize();
    }
    MfEnvironment(const MfEnvironment&)=delete;
    MfEnvironment& operator=(const MfEnvironment&)=delete;
};

struct Writer {
    ComPtr<IMFSinkWriter> writer;
    DWORD stream = 0;
};
Writer OpenSink(const std::wstring& filename) {
    ComPtr<IMFAttributes> config;
    Check("MFCreateAttributes", MFCreateAttributes(config.GetAddressOf(), 2));
    Check("MF_TRANSCODE_CONTAINERTYPE", config->SetGUID(
        MF_TRANSCODE_CONTAINERTYPE, MFTranscodeContainerType_MPEG4));
    Check("Disable hardware MFT preference", config->SetUINT32(
        MF_READWRITE_ENABLE_HARDWARE_TRANSFORMS, FALSE));
    Writer output;
    Check("MFCreateSinkWriterFromURL", MFCreateSinkWriterFromURL(
        filename.c_str(), nullptr, config.Get(), output.writer.GetAddressOf()));

    ComPtr<IMFMediaType> encoded;
    Check("MFCreateMediaType encoded", MFCreateMediaType(encoded.GetAddressOf()));
    Check("Output major type", encoded->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video));
    Check("Output H264", encoded->SetGUID(MF_MT_SUBTYPE, MFVideoFormat_H264));
    Check("Output bitrate", encoded->SetUINT32(MF_MT_AVG_BITRATE, 2'500'000));
    Check("Output progressive", encoded->SetUINT32(
        MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive));
    Check("Output size", MFSetAttributeSize(encoded.Get(), MF_MT_FRAME_SIZE, p0::W, p0::H));
    Check("Output fps", MFSetAttributeRatio(encoded.Get(), MF_MT_FRAME_RATE, p0::FPS, 1));
    Check("Output PAR", MFSetAttributeRatio(encoded.Get(), MF_MT_PIXEL_ASPECT_RATIO, 1, 1));
    Check("AddStream", output.writer->AddStream(encoded.Get(), &output.stream));

    ComPtr<IMFMediaType> raw;
    Check("MFCreateMediaType raw", MFCreateMediaType(raw.GetAddressOf()));
    Check("Input major type", raw->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video));
    Check("Input RGB32", raw->SetGUID(MF_MT_SUBTYPE, MFVideoFormat_RGB32));
    Check("Input progressive", raw->SetUINT32(
        MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive));
    Check("Input size", MFSetAttributeSize(raw.Get(), MF_MT_FRAME_SIZE, p0::W, p0::H));
    Check("Input fps", MFSetAttributeRatio(raw.Get(), MF_MT_FRAME_RATE, p0::FPS, 1));
    Check("Input PAR", MFSetAttributeRatio(raw.Get(), MF_MT_PIXEL_ASPECT_RATIO, 1, 1));

    // This is the negotiation experiment: the H.264 MFT does NOT itself accept
    // RGB32; Sink Writer may insert a converter. If not, fail closed here.
    Check("SetInputMediaType RGB32->H264 negotiation",
          output.writer->SetInputMediaType(output.stream, raw.Get(), nullptr));
    Check("BeginWriting", output.writer->BeginWriting());
    return output;
}

void SendFrame(Writer& output, std::uint32_t index) {
    const auto frame=p0::MakePattern(index);
    const auto byteCount=static_cast<DWORD>(frame.size()*sizeof(frame[0]));
    ComPtr<IMFMediaBuffer> buffer;
    Check("MFCreateMemoryBuffer", MFCreateMemoryBuffer(byteCount,buffer.GetAddressOf()));
    BYTE* data=nullptr;
    Check("IMFMediaBuffer::Lock", buffer->Lock(&data, nullptr, nullptr));
    std::memcpy(data,frame.data(),byteCount);
    const HRESULT unlockHr=buffer->Unlock();
    Check("IMFMediaBuffer::Unlock",unlockHr);
    Check("SetCurrentLength",buffer->SetCurrentLength(byteCount));
    ComPtr<IMFSample> sample;
    Check("MFCreateSample",MFCreateSample(sample.GetAddressOf()));
    Check("AddBuffer",sample->AddBuffer(buffer.Get()));
    Check("SetSampleTime",sample->SetSampleTime(p0::Tick(index,p0::TEST_FRAMES)));
    Check("SetSampleDuration",sample->SetSampleDuration(p0::Duration(index,p0::TEST_FRAMES)));
    Check("WriteSample",output.writer->WriteSample(output.stream,sample.Get()));
}

// This TU is compiled as an OBJECT library even in the default OFF build.
// It is NOT linked to the executable when media output is disabled.
int RunExperimentalMedia() {
    try {
        const auto outputDir = fs::current_path() / L"mf_p0_output";
        if (fs::is_symlink(outputDir))
            throw std::runtime_error("Refuse symlinked output directory");
        if (fs::exists(outputDir) && !fs::is_directory(outputDir))
            throw std::runtime_error("Output destination is not a directory");
        if (!fs::exists(outputDir)) fs::create_directory(outputDir);
        const auto outputFile=outputDir / L"MF-P0_UNVERIFIED_EXPERIMENT.mp4";
        if (fs::exists(outputFile)) throw std::runtime_error("Will not overwrite an existing file");
        MfEnvironment env;
        Writer writer=OpenSink(outputFile.wstring());
        for (std::uint32_t index=0; index<p0::TEST_FRAMES; ++index)
            SendFrame(writer,index);
        Check("Finalize",writer.writer->Finalize());
        std::wcout << L"WRITER FINALIZE RETURNED SUCCESS; MP4 IS NOT VERIFIED.\n"
                   << L"Destination: " << outputFile.wstring() << L"\n"
                   << L"Physical process termination, decode and Policy B NOT demonstrated.\n";
        return 0;
    } catch(const std::exception& e) {
        std::cerr << "MF-P0 FAILED CLOSED: " << e.what() << "\n"
                  << "Any partial file remains unverified; no automatic promotion.\n";
        return 1;
    }
}
