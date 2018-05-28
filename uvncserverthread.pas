unit UVNCServerThread;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Process
  {$IFDEF WINDOWS}
    , jwatlhelp32, Windows
  {$ENDIF}
  ;

type
  TVNCServerThread = class(TThread)
    private
      passwd, passwd2: string;
      shouldTerminate: boolean;
    protected
      procedure execute; override;
    public
      constructor create(cpasswd, cpasswd2: string);
      procedure kill;
  end;

implementation

constructor TVNCServerThread.create(cpasswd, cpasswd2: string);
begin
  passwd:=cpasswd;
  passwd2:=cpasswd2;
  shouldTerminate:=false;
  FreeOnTerminate:=true;
  inherited create(false);
end;

procedure TVNCServerThread.kill;
begin
  shouldTerminate:=true;
end;

procedure TVNCServerThread.execute;
var
  myProcess: TProcess;
begin
  {$IFDEF WINDOWS}
    myProcess:=TProcess.create(nil);
    myProcess.executable:='C:\Program Files\PhilleConnect\vnc\winvncstartup.exe';
    myProcess.parameters.add(passwd);
    myProcess.parameters.add(passwd2);
    myProcess.showWindow:=swoHIDE;
    myProcess.execute;
    myProcess.waitOnExit;
    myProcess.free;
    myProcess:=TProcess.create(nil);
    myProcess.executable:='C:\Program Files\PhilleConnect\vnc\winvnc.exe';
    myProcess.execute;
  {$ENDIF}
  {$IFDEF LINUX}
    myProcess:=TProcess.create(nil);
    myProcess.executable:='sh';
    myProcess.parameters.add('-c');
    myProcess.parameters.add('x11vnc -o /tmp/x11vnc.log -storepasswd '+passwd+' /tmp/philleconnectpasswd');
    myProcess.execute;
    myProcess.waitOnExit;
    myProcess.free;
    myProcess:=TProcess.create(nil);
    myProcess.executable:='sh';
    myProcess.parameters.add('-c');
    myProcess.parameters.add('x11vnc -rfbauth /tmp/philleconnectpasswd -o /tmp/x11vnc.log');
    myProcess.execute;
  {$ENDIF}
  while (not shouldTerminate) do begin
    sleep(10);
  end;
  myProcess.terminate(0);
  myProcess.free;
end;

end.

