unit ULockscreen;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, FileUtil, Forms, Controls, Graphics, Dialogs, StdCtrls,
  ExtCtrls, fphttpserver, UGetMacAdress, UGetIpAdress, fpjson, jsonparser,
  HTTPSend, Process, ssl_openssl, UVNCServerThread, LCLIntf, LCLType, base64,
  {$IFDEF WINDOWS}
    UCreateWatchdogThread, ULockCAENTF,
  {$ENDIF}
  UPingThread, resolve;

type

  { TLockscreen }

  TLockscreen = class(TForm)
    lockLabel: TLabel;
    reloadTimer: TTimer;
    lockscreenTimer: TTimer;
    procedure FormCloseQuery(Sender: TObject; var CanClose: boolean);
    procedure FormCreate(Sender: TObject);
    procedure reloadTimerTimer(Sender: TObject);
    procedure lockscreenTimerTimer(Sender: TObject);
  private
    //System herunterfahren
    procedure shutdown;
    //Netzwerkverbindung prüfen
    procedure checkNetworkConnection;
    procedure networkConnectionResult(result: boolean; return: string);
    procedure trueNetworkResult;
    procedure falseNetworkResult;
    //Konfiguration laden
    procedure loadConfig;
    function createScreenshot: TStringStream;
    function randomString(wantedLength: integer): string;
    function sendRequest(url, params: string): string;
    function MemStreamToString(Strm: TMemoryStream): AnsiString;
    function ValidateIP(IP4: string): Boolean;
  public
    procedure DoHandleRequest(Sender:TObject; var ARequest:TFPHTTPConnectionRequest; var AResponse:TFPHTTPConnectionResponse);
  end;

  THTTPServerThread = class(TThread)
  private
    Fserver : TFPHTTPServer;
  public
    constructor Create(APort:Word; const OnRequest:THTTPServerRequestHandler);
    procedure Execute; override;
    procedure DoTerminate; override;
    property Server : TFPHTTPServer read FServer;
  end;
  //DLL-Funktionen
  {$IFDEF WINDOWS}
    function InstallHook(Hwnd: THandle; strictParam: boolean): boolean; stdcall; external 'hook.dll';
    function UninstallHook: boolean; stdcall; external 'hook.dll';
    function ControlHook(mode: boolean): boolean; stdcall; external 'hook.dll';
    function InstallMouseHook(Hwnd: THandle): boolean; stdcall; external 'mhook.dll';
    function UninstallMouseHook: boolean; stdcall; external 'mhook.dll';
    function ControlMouseHook(mode: boolean): boolean; stdcall; external 'mhook.dll';
  {$ENDIF}

var
  Lockscreen: TLockscreen;
  FServerThread: THTTPServerThread;
  room, machinename, serverURL, globalPW, mac, ip, response, os,
  cleanServerURL: string;
  MacAddr: TGetMacAdress;
  IPAddr: TGetIPAdress;
  config, value: TStringList;
  c: integer;
  jData: TJSONData;
  VNCServer: TVNCServerThread;
  {$IFDEF WINDOWS}
    watchdog: TCreateWatchdogThread;
    lockCA: TLockCAENTF;
  {$ENDIF}
  pingthread: TPingThread;
  locked, isOnline, lockscreenIsVisible: boolean;

implementation

{$R *.lfm}

{ TLockscreen }

procedure TLockscreen.FormCreate(Sender: TObject);
begin
  {$IFDEF LINUX}
    if (ParamStr(1) = 'screenshot') then begin
      WriteLn(EncodeStringBase64(createScreenshot().dataString));
      halt;
    end
    else begin
  {$ENDIF}
  locked:=false;
  {$IFDEF WINDOWS}
    watchdog:=TCreateWatchdogThread.create(ParamStr(1));
    lockscreen.windowState:=wsMaximized;
  {$ENDIF}
  {$IFDEF LINUX}
    lockscreen.windowState:=wsFullScreen;
  {$ENDIF}
  config:=TStringList.create;
  isOnline:=false;
  {$IFDEF WINDOWS}
    InstallHook(handle, true);
    InstallMouseHook(handle);
    config.loadFromFile('C:\Program Files\PhilleConnect\pcconfig.jkm');
  {$ENDIF}
  {$IFDEF LINUX}
    config.loadFromFile('/etc/pcconfig.jkm');
  {$ENDIF}
  c:=0;
  while (c < config.count) do begin
    if (pos('#', config[c]) = 0) then begin
      value:=TStringList.create;
      value.clear;
      value.strictDelimiter:=true;
      value.delimiter:='=';
      value.delimitedText:=config[c];
      case value[0] of
        'server':
          serverURL:=value[1];
        'global':
          globalPW:=value[1];
      end;
    end;
    c:=c+1;
  end;
  checkNetworkConnection;
  {$IFDEF LINUX}
    end;
  {$ENDIF}
end;

procedure TLockscreen.FormCloseQuery(Sender: TObject; var CanClose: boolean);
begin
  {$IFDEF WINDOWS}
    UninstallHook;
    UninstallMouseHook;
  {$ENDIF}
end;

procedure TLockscreen.checkNetworkConnection;
var
  noPort: TStringList;
  cache: string;
begin
  if (pos(':', serverURL) > 0) then begin
    noPort:=TStringList.create;
    noPort.delimiter:=':';
    noPort.strictDelimiter:=true;
    noPort.delimitedText:=serverURL;
    cache:=noPort[0];
  end
  else begin
    cache:=serverURL;
  end;
  cleanServerURL:=cache;
  pingthread:=TPingThread.create(cache);
  pingthread.OnShowStatus:=@networkConnectionResult;
  pingthread.resume;
end;

procedure TLockscreen.networkConnectionResult(result: boolean; return: string);
var
  host: THostResolver;
begin
  if (result) then begin
    if (ValidateIP(cleanServerURL)) then begin
      if (cleanServerURL = return) then begin
        trueNetworkResult;
      end
      else begin
        falseNetworkResult;
      end;
    end
    else begin
      host:=THostResolver.create(nil);
      host.clearData();
      if (host.NameLookup(cleanServerURL)) then begin
        if (host.AddressAsString = return) then begin
          trueNetworkResult;
        end
        else begin
          falseNetworkResult;
        end;
      end
      else begin
        falseNetworkResult;
      end;
    end;
  end
  else begin
    falseNetworkResult;
  end;
end;

procedure TLockscreen.trueNetworkResult;
begin
  reloadTimer.enabled:=false;
  if not(isOnline) then begin
    loadConfig;
  end;
  isOnline:=true;
end;

procedure TLockscreen.falseNetworkResult;
begin
  reloadTimer.enabled:=true;
end;

procedure TLockscreen.loadConfig;
begin
  MacAddr:=TGetMacAdress.create;
  mac:=MacAddr.getMac;
  MacAddr.free;
  IPAddr:=TGetIPAdress.create;
  ip:=IPAddr.getIP;
  IPAddr.free;
  {$IFDEF WINDOWS}
    os:='win';
  {$ENDIF}
  {$IFDEF LINUX}
    os:='linux';
  {$ENDIF}
  response:=SendRequest('https://'+serverURL+'/client.php', 'usage=config&globalpw='+globalPW+'&machine='+mac+'&ip='+ip+'&os='+os);
  if (response = '!') then begin
    showMessage('Konfigurationsfehler');
  end
  else if (response = 'nomachine') then begin
    showMessage('Rechner nicht registriert');
  end
  else if (response <> '') then begin
    reloadTimer.Enabled:=false;
    jData:=GetJSON(response);
    c:=0;
    while (c < jData.count) do begin
      case jData.FindPath(IntToStr(c)+'[0]').AsString of
        'machinename':
          machinename:=jData.FindPath(IntToStr(c)+'[1]').AsString;
        'room':
          room:=jData.FindPath(IntToStr(c)+'[1]').AsString;
      end;
      c:=c+1;
    end;
    FServerThread:=THTTPServerThread.Create(34567, @DoHandleRequest);
    FServerThread.Start;
  end
  else begin
    reloadTimer.enabled:=true;
  end;
end;

procedure TLockscreen.reloadTimerTimer(Sender: TObject);
begin
  checkNetworkConnection;
end;

procedure TLockscreen.lockscreenTimerTimer(Sender: TObject);
begin
  if (lockscreenIsVisible) then begin
    lockscreen.visible:=true;
  end
  else begin
    lockscreen.visible:=false;
  end;
  lockscreenTimer.enabled:=false;
end;

procedure TLockscreen.DoHandleRequest(Sender: TObject;
  var ARequest: TFPHTTPConnectionRequest; var AResponse: TFPHTTPConnectionResponse);
var
  params: TStringList;
  response, vncpassword: string;
  {$IFDEF LINUX}
    scProcess: TProcess;
    scResponse: TStringList;
  {$ENDIF}
begin
  params:=TStringList.create;
  params.delimiter:='/';
  params.delimitedText:=ARequest.url;
  response:=SendRequest('https://'+serverURL+'/client.php', 'usage=checkteacher&globalpw='+globalPW+'&machine='+mac+'&ip='+ip+'&os='+os+'&req='+ARequest.remoteAddress);
  if (params[1] = 'online') then begin
    AResponse.content:='online';
  end
  else if (params[1] = room) and (params[2] = machinename) and (response = 'success') then begin
    if (params[3] = 'lock') then begin
      if (locked = false) then begin
        {$IFDEF WINDOWS}
          lockscreen.Visible:=true;
          ControlHook(true);
          ControlMouseHook(true);
          lockCA:=TLockCAENTF.create;
        {$ENDIF}
        {$IFDEF LINUX}
          lockscreenIsVisible:=true;
          lockscreenTimer.enabled:=true;
        {$ENDIF}
      end;
      locked:=true;
      AResponse.content:='locked';
    end
    else if (params[3] = 'unlock') then begin
      if (locked = true) then begin
        {$IFDEF WINDOWS}
          lockscreen.visible:=false;
          ControlHook(false);
          ControlMouseHook(false);
          lockCA.disable;
          lockCA.free;
        {$ENDIF}
        {$IFDEF LINUX}
          lockscreenIsVisible:=false;
          lockscreenTimer.enabled:=true;
        {$ENDIF}
      end;
      locked:=false;
      AResponse.content:='unlocked';
    end
    else if (params[3] = 'shutdown') then begin
      AResponse.content:='shutdown';
      shutDown;
    end
    else if (params[3] = 'screenshot') then begin
      {$IFDEF WINDOWS}
        AResponse.content:=EncodeStringBase64(createScreenshot().dataString);
      {$ENDIF}
      {$IFDEF LINUX}
        scProcess:=TProcess.create(nil);
        scProcess.executable:='sh';
        scProcess.parameters.add('-c');
        scProcess.parameters.add('systemclient screenshot');
        scProcess.options:=scProcess.options + [poWaitOnExit, poUsePipes];
        scProcess.execute;
        scResponse:=TStringList.create;
        scResponse.loadFromStream(scProcess.output);
        AResponse.content:=scResponse.commaText;
        scProcess.free;
        scResponse.free;
      {$ENDIF}
    end
    else if (params[3] = 'requestcontrol') then begin
      vncpassword:=randomString(8);
      AResponse.content:=vncpassword;
      VNCServer:=TVNCServerThread.create(vncpassword, randomString(8));
    end
    else if (params[3] = 'cancelcontrol') then begin
      VNCServer.kill;
      AResponse.content:='success';
    end;
  end
  else if (params[1] = 'lockstate') then begin
    if (locked = true) then begin
      AResponse.content:='locked';
    end
    else begin
      AResponse.content:='unlocked';
    end;
  end;
end;

procedure TLockscreen.shutdown;
var
  shutdownProcess: TProcess;
begin
  shutdownProcess:=TProcess.create(nil);
  shutdownProcess.executable:='cmd';
  shutdownProcess.parameters.add('/C shutdown /s /f /t 0');
  shutdownProcess.showWindow:=swoHIDE;
  shutdownProcess.execute;
  shutdownProcess.free;
end;

function TLockscreen.createScreenshot: TStringStream;
var
  SBitmap: TBitmap;
  Image: TJPEGImage;
  ScreenDC: HDC;
begin
  SBitmap:=TBitmap.create;
  ScreenDC:=GetDC(0);
  SBitmap.setSize(Screen.width, Screen.height);
  SBitmap.loadFromDevice(ScreenDC);
  ReleaseDC(0, ScreenDC);
  Image:=TJPEGImage.create;
  Image.CompressionQuality:=5;
  Image.Assign(SBitmap);
  SBitmap.free;
  Result:=TStringStream.create('');
  Image.saveToStream(Result);
  Image.free;
end;

function TLockscreen.randomString(wantedLength: integer): string;
var
  str: string;
begin
  randomize;
  str:='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?=+-~@';
  result:='';
  repeat
    result:=result + str[random(Length(str)) + 1];
  until(Length(result) = wantedLength)
end;

function TLockscreen.sendRequest(url, params: string): string;
var
  Response: TMemoryStream;
begin
  Response := TMemoryStream.Create;
  try
    if HttpPostURL(url, params, Response) then
      result:=MemStreamToString(Response);
  finally
    Response.Free;
  end;
end;

function TLockscreen.MemStreamToString(Strm: TMemoryStream): AnsiString;
begin
  if Strm <> nil then begin
    Strm.Position := 0;
    SetString(Result, PChar(Strm.Memory), Strm.Size);
  end;
end;

function TLockscreen.ValidateIP(IP4: string): Boolean; // Coding by Dave Sonsalla
var
  Octet : String;
  Dots, I : Integer;
begin
  IP4 := IP4+'.'; //add a dot. We use a dot to trigger the Octet check, so need the last one
  Dots := 0;
  Octet := '0';
  for I := 1 to length(IP4) do begin
    if IP4[I] in ['0'..'9','.'] then begin
      if IP4[I] = '.' then begin //found a dot so inc dots and check octet value
        Inc(Dots);
        if (length(Octet) =1) Or (StrToInt(Octet) > 255) then Dots := 5; //Either there's no number or it's higher than 255 so push dots out of range
        Octet := '0'; // Reset to check the next octet
      end // End of IP4[I] is a dot
      else // Else IP4[I] is not a dot so
        Octet := Octet + IP4[I]; // Add the next character to the octet
    end // End of IP4[I] is not a dot
    else // Else IP4[I] Is not in CheckSet so
      Dots := 5; // Push dots out of range
  end;
  result := (Dots = 4) // The only way that Dots will equal 4 is if we passed all the tests
end;

constructor THTTPServerThread.Create(APort: Word;
  const OnRequest: THTTPServerRequestHandler);
begin
  inherited create(true);
  FreeAndNil(FServer);
  FServer:=TFPHTTPServer.Create(nil);
  FServer.Threaded:=true;
  FServer.Port:=APort;
  FServer.OnRequest:=OnRequest;
end;

procedure THTTPServerThread.Execute;
begin
  try
    FServer.Active:=true;
    while not terminated do sleep(10);
  finally
    FreeAndNil(FServer);
  end;
end;

procedure THTTPServerThread.DoTerminate;
begin
  inherited DoTerminate;
  FServer.Active:=false;
end;

end.

