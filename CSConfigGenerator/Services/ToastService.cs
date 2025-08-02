namespace CSConfigGenerator.Services;

public class ToastService : IDisposable
{
    public event Action<string, ToastLevel>? OnShow;
    public event Action? OnHide;

    public void ShowToast(string message, ToastLevel level = ToastLevel.Info)
    {
        OnShow?.Invoke(message, level);
    }

    public void HideToast()
    {
        OnHide?.Invoke();
    }

    public void Dispose()
    {
        OnShow = null;
        OnHide = null;
    }
}

public enum ToastLevel
{
    Info,
    Success,
    Warning,
    Error
}
