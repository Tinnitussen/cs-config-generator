namespace CSConfigGenerator.Models;
public interface ISettingOperations
{
    void UpdateValue(object value);
    void Add();
    void Remove();
    void Restore();
}