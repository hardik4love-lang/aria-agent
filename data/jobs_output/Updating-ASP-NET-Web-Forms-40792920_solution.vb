' Modernization Wrapper for Legacy VB.NET WebForms
Imports System.Data.SqlClient

Public Class LegacyModernizer
    Public Shared Function FetchRecordsSafely(ByVal connectionString As String, ByVal categoryId As Integer) As DataTable
        Dim dt As New DataTable()
        Dim query As String = "SELECT Id, Name, Price, Status FROM Products WHERE CategoryId = @catId ORDER BY Id DESC"
        
        Using conn As New SqlConnection(connectionString)
            Using cmd As New SqlCommand(query, conn)
                cmd.Parameters.AddWithValue("@catId", categoryId)
                Using adapter As New SqlDataAdapter(cmd)
                    adapter.Fill(dt)
                End Using
            End Using
        End Using
        Return dt
    End Function
End Class
