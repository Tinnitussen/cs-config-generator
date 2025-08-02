using CSConfigGenerator.Models;

namespace CSConfigGenerator.Interfaces;

public interface IToastService
{
    event Action<string, ToastLevel>? OnShow;
    event Action? OnHide;
    void ShowToast(string message, ToastLevel level = ToastLevel.Info);
    void HideToast();
}
