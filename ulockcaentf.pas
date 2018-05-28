unit ULockCAENTF;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Registry;

type
  TLockCAENTF = class
    public
      constructor create;
      procedure disable;
  end;

implementation

constructor TLockCAENTF.create;
var
  registry: TRegistry;
begin
  registry:=TRegistry.create;
  registry.RootKey:=HKEY_CURRENT_USER;
  registry.OpenKey('Software\Microsoft\Windows\CurrentVersion\Policies\System', true);
  registry.writeInteger('DisableLockWorkstation', 1);
  registry.writeInteger('HideFastUserSwitching', 1);
  registry.writeInteger('DisableChangePassword', 1);
  registry.writeInteger('DisableTaskMgr', 1);
  registry.free;
  registry:=TRegistry.create;
  registry.RootKey:=HKEY_CURRENT_USER;
  registry.OpenKey('Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', true);
  registry.writeInteger('NoLogoff', 1);
  registry.free;
end;

procedure TLockCAENTF.disable;
var
  registry: TRegistry;
begin
  registry:=TRegistry.create;
  registry.RootKey:=HKEY_CURRENT_USER;
  registry.OpenKey('Software\Microsoft\Windows\CurrentVersion\Policies\System', true);
  registry.writeInteger('DisableLockWorkstation', 0);
  registry.writeInteger('HideFastUserSwitching', 0);
  registry.writeInteger('DisableChangePassword', 0);
  registry.writeInteger('DisableTaskMgr', 0);
  registry.free;
  registry:=TRegistry.create;
  registry.RootKey:=HKEY_CURRENT_USER;
  registry.OpenKey('Software\Microsoft\Windows\CurrentVersion\Policies\Explorer', true);
  registry.writeInteger('NoLogoff', 0);
  registry.free;
end;

end.

