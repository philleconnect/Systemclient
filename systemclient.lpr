program systemclient;

{$mode objfpc}{$H+}

uses
  {$IFDEF UNIX}
  cthreads,
  {$ENDIF}
  Interfaces, // this includes the LCL widgetset
  Forms, ULockscreen, ULockCAENTF
  { you can add units after this };

{$R *.res}

begin
  RequireDerivedFormResource:=True;
  Application.Initialize;
  Application.ShowMainForm:=False;
  Application.CreateForm(TLockscreen, Lockscreen);
  Application.Run;
end.

