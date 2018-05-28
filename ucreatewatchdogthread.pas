unit UCreateWatchdogThread;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Process, jwatlhelp32, Windows;

type
  TCreateWatchdogThread = class(TThread)
    private
      givenPid: integer;
    protected
      procedure execute; override;
    public
      constructor create(given: string);
  end;

implementation

constructor TCreateWatchdogThread.create(given: string);
begin
  FreeOnTerminate:=true;
  if (given = '') then begin
    givenPid:=0;
  end
  else begin
    givenPid:=StrToInt(given);
  end;
  inherited create(false);
end;

procedure TCreateWatchdogThread.execute;
var
  ContinueLoop: boolean;
  FSnapshotHandle: THandle;
  FProcessEntry32: TProcessEntry32;
  foundProcess: boolean;
  myProcess: TProcess;
  DKMPPID: integer;
begin
  if (givenPid = 0) then begin
    myProcess:=TProcess.create(nil);
    myProcess.executable:='C:\Program Files\PhilleConnect\DKMP.exe';
    myProcess.parameters.add('startWatchdogAndKill');
    myProcess.showWindow:=swoHIDE;
    myProcess.execute;
    myProcess.waitOnExit;
    DKMPPID:=myProcess.exitStatus;
    myProcess.free;
  end
  else begin
    DKMPPID:=givenPid;
  end;
  while true do begin
    FSnapshotHandle := CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    FProcessEntry32.dwSize := SizeOf(FProcessEntry32);
    ContinueLoop := Process32First(FSnapshotHandle, FProcessEntry32);
    foundProcess:=false;
    while ContinueLoop do
    begin
      if (FProcessEntry32.th32ProcessId = DKMPPID) then
      begin
        foundProcess:=true;
      end;
      ContinueLoop := Process32Next(FSnapshotHandle, FProcessEntry32);
    end;
    CloseHandle(FSnapshotHandle);
    if not(foundProcess) then begin
      myProcess:=TProcess.create(nil);
      myProcess.executable:='C:\Program Files\PhilleConnect\DKMP.exe';
      myProcess.parameters.add('startWatchdogAndKill');
      myProcess.parameters.add(IntToStr(getProcessId));
      myProcess.showWindow:=swoHIDE;
      myProcess.execute;
      myProcess.waitOnExit;
      DKMPPID:=myProcess.exitStatus;
      myProcess.free;
    end;
    sleep(50);
  end;
end;

end.

