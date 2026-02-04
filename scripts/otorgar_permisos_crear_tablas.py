#!/usr/bin/env python3
"""
Script para otorgar permisos de BigQuery Data Editor al usuario actual.
Usa Application Default Credentials.
"""
import os
import sys

try:
    from google.cloud import resourcemanager
    from google.oauth2 import default
    from googleapiclient.discovery import build
except ImportError:
    print("❌ ERROR: Faltan dependencias de Google Cloud")
    print("")
    print("Instala con:")
    print("  pip install google-cloud-resource-manager google-api-python-client")
    sys.exit(1)

PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'brave-computer-454217-q4')
ROLE = 'roles/bigquery.dataEditor'

def get_current_user_email():
    """Obtiene el email del usuario autenticado."""
    try:
        credentials, project = default()
        # Intentar obtener el email de las credenciales
        if hasattr(credentials, 'service_account_email'):
            return credentials.service_account_email
        elif hasattr(credentials, 'token'):
            # Para OAuth, necesitamos hacer una llamada a la API
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info.get('email')
    except Exception as e:
        print(f"⚠️  No se pudo obtener email automáticamente: {e}")
        return None

def grant_bigquery_data_editor():
    """Otorga el rol BigQuery Data Editor al usuario actual."""
    try:
        # Obtener credenciales
        credentials, project = default()
        
        # Construir el servicio de Cloud Resource Manager
        service = build('cloudresourcemanager', 'v1', credentials=credentials)
        
        # Obtener el email del usuario
        user_email = get_current_user_email()
        
        if not user_email:
            print("❌ No se pudo determinar el email del usuario")
            print("")
            print("Por favor, ejecuta manualmente desde la consola:")
            print(f"  1. Ve a: https://console.cloud.google.com/iam-admin/iam?project={PROJECT_ID}")
            print(f"  2. Busca tu email y agrega el rol: BigQuery Data Editor")
            return False
        
        print(f"🔐 Otorgando permisos de BigQuery Data Editor...")
        print(f"   Usuario: {user_email}")
        print(f"   Proyecto: {PROJECT_ID}")
        print(f"   Rol: {ROLE}")
        print("")
        
        # Obtener la política IAM actual
        policy = service.projects().getIamPolicy(
            resource=PROJECT_ID,
            body={}
        ).execute()
        
        # Verificar si el binding ya existe
        binding_exists = False
        for binding in policy.get('bindings', []):
            if binding['role'] == ROLE:
                if f"user:{user_email}" in binding.get('members', []):
                    print(f"✅ El usuario ya tiene el rol {ROLE}")
                    return True
                # Agregar el usuario al binding existente
                binding['members'].append(f"user:{user_email}")
                binding_exists = True
                break
        
        # Si no existe el binding, crear uno nuevo
        if not binding_exists:
            policy.setdefault('bindings', []).append({
                'role': ROLE,
                'members': [f"user:{user_email}"]
            })
        
        # Aplicar la política actualizada
        service.projects().setIamPolicy(
            resource=PROJECT_ID,
            body={'policy': policy}
        ).execute()
        
        print(f"✅ Permisos otorgados exitosamente")
        print("")
        print("⏳ Espera 10-30 segundos para que los permisos se propaguen")
        print("   Luego intenta ejecutar la query CREATE TABLE de nuevo")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error otorgando permisos: {error_msg}")
        print("")
        print("═══════════════════════════════════════════════════════════════════════")
        print("   SOLUCIÓN MANUAL:")
        print("═══════════════════════════════════════════════════════════════════════")
        print("")
        print(f"1. Ve a: https://console.cloud.google.com/iam-admin/iam?project={PROJECT_ID}")
        print("")
        print("2. Busca tu email en la lista de miembros")
        print("")
        print("3. Si no estás en la lista, click en 'GRANT ACCESS' y agrega tu email")
        print("")
        print("4. Agrega el rol: BigQuery Data Editor")
        print("")
        print("5. Guarda y espera 10-30 segundos")
        print("")
        print("6. Vuelve a BigQuery Console y ejecuta la query CREATE TABLE")
        print("")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("  OTORGAR PERMISOS BIGQUERY DATA EDITOR")
    print("=" * 70)
    print("")
    
    success = grant_bigquery_data_editor()
    
    if not success:
        sys.exit(1)
